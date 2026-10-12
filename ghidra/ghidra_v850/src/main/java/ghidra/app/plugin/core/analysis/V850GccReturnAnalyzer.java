package ghidra.app.plugin.core.analysis;

import java.io.IOException;
import org.xml.sax.SAXException;

import ghidra.app.services.AbstractAnalyzer;
import ghidra.app.services.AnalysisPriority;
import ghidra.app.services.AnalyzerType;
import ghidra.app.util.importer.MessageLog;
import ghidra.framework.options.Options;
import ghidra.framework.store.LockException;
import ghidra.program.database.SpecExtension;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.Array;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeComponent;
import ghidra.program.model.data.Structure;
import ghidra.program.model.data.TypeDef;
import ghidra.program.model.lang.PrototypeModel;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Program;
import ghidra.program.model.pcode.XmlEncode;
import ghidra.util.exception.AssertException;
import ghidra.util.exception.CancelledException;
import ghidra.util.exception.InvalidInputException;
import ghidra.util.task.TaskMonitor;
import ghidra.xml.XmlParseException;

/** Old-GCC aggregate return layout, including subsequent signature edits. */
public class V850GccReturnAnalyzer extends AbstractAnalyzer {
	private static final String GCC_INDIRECT_CONVENTION_PREFIX = "__v850_gcc_sret";

	public V850GccReturnAnalyzer() {
		super("V850 GCC aggregate returns", "Recover field-layout-dependent old-GCC return ABI",
			AnalyzerType.FUNCTION_SIGNATURES_ANALYZER);
		setDefaultEnablement(true);
		setPriority(AnalysisPriority.FUNCTION_ANALYSIS.after());
	}

	@Override
	public boolean canAnalyze(Program program) {
		return "v850".equals(program.getLanguage().getProcessor().toString());
	}

	@Override
	public boolean added(Program program, AddressSetView set, TaskMonitor monitor, MessageLog log)
			throws CancelledException {
		FunctionIterator functions = program.getFunctionManager().getFunctions(set, true);
		while (functions.hasNext()) {
			monitor.checkCancelled();
			applyToFunction(program, functions.next(), monitor);
		}
		return true;
	}
	private static void ensureConventionInstalled(Program program, String name, TaskMonitor monitor)
			throws LockException, IOException, XmlParseException, SAXException, CancelledException {
		Options specOptions = program.getOptions(SpecExtension.SPEC_EXTENSION);
		String optionName = "prototype_" + name;
		String xml = buildPrototypeXml(program, name);
		if (xml.equals(specOptions.getString(optionName, null))) {
			return; // identical extension already installed
		}
		new SpecExtension(program).addReplaceCompilerSpecExtension(xml, monitor);
	}

	private static String buildPrototypeXml(Program program, String name)
			throws IOException {
		PrototypeModel def = program.getCompilerSpec().getDefaultCallingConvention();
		XmlEncode encoder = new XmlEncode();
		def.encode(encoder, program.getCompilerSpec().getPcodeInjectLibrary());
		String encoded = encoder.toString();
		int nameStart = encoded.indexOf("name=\"") + "name=\"".length();
		int nameEnd = encoded.indexOf('\"', nameStart);
		if (nameStart < "name=\"".length() || nameEnd < nameStart) {
			throw new IOException("cannot extract default prototype name");
		}
		String xml = encoded.substring(0, nameStart) + name + encoded.substring(nameEnd);
		int outputStart = xml.indexOf("<output");
		int outputBody = xml.indexOf('>', outputStart) + 1;
		if (outputStart < 0 || outputBody <= outputStart) {
			throw new IOException("cannot extract default prototype output");
		}
		int outputEnd = xml.indexOf("</output>", outputBody);
		if (outputEnd < 0) {
			throw new IOException("cannot locate default prototype output end");
		}
		// The extension document is validated against the same compiler_spec
		// grammar as installed cspecs. Two 12.1.4 constraints apply:
		//   - <hidden_return> accepts only voidlock, not strategy="normalparam";
		//     the plain form still allocates the buffer pointer from the first
		//     general-purpose input entry (r6) with the r6->r10 pointer echo.
		//   - within <output>, every <pentry> must precede the first <rule>,
		//     so splice ahead of the base rules, never ahead of the pentries.
		// Placing this rule first also makes struct returns of ANY size take
		// the hidden buffer, before the size-filtered base hidden-return and
		// join rules can claim small aggregates.
		int insertAt = xml.indexOf("<rule>", outputBody);
		if (insertAt < 0 || insertAt > outputEnd) {
			insertAt = outputEnd;
		}
		return xml.substring(0, insertAt) +
			"<rule><datatype name=\"struct\"/><hidden_return/></rule>" +
			xml.substring(insertAt);
	}

	public static boolean usesOldGcc(Program program) {
		String id = program.getCompilerSpec().getCompilerSpecID().toString();
		return id.equals("gcc") || id.startsWith("gcc-callee-");
	}

	/**
	 * Old GCC returns only a union, one flattened field, or two flattened
	 * fields whose second field starts at byte four in r10:r11. Other small
	 * structs need the same hidden r6 buffer/r10 pointer return as large ones.
	 * SDK nec850/tinfo.cpp should_pass_struct_by_value supplies this layout rule.
	 */
	private static boolean needsGccIndirectReturn(DataType type) {
		while (type instanceof TypeDef typedef) {
			type = typedef.getBaseDataType();
		}
		if (!(type instanceof Structure) || type.getLength() > 8) {
			return false;
		}
		GccReturnShape shape = new GccReturnShape();
		if (!shape.flatten(type, 0)) {
			return true;
		}
		return shape.count == 0 || shape.firstOffset != 0 ||
			(shape.count == 2 && shape.secondOffset != 4);
	}

	private static final class GccReturnShape {
		int count;
		int firstOffset;
		int secondOffset;

		boolean flatten(DataType type, int offset) {
			while (type instanceof TypeDef typedef) {
				type = typedef.getBaseDataType();
			}
			if (type instanceof Structure structure) {
				for (DataTypeComponent component : structure.getDefinedComponents()) {
					if (!flatten(component.getDataType(), offset + component.getOffset())) {
						return false;
					}
				}
				return true;
			}
			if (type instanceof Array array) {
				for (int index = 0; index < array.getNumElements(); index++) {
					if (!flatten(array.getDataType(), offset + index * array.getElementLength())) {
						return false;
					}
				}
				return true;
			}
			if (++count > 2) {
				return false;
			}
			if (count == 1) {
				firstOffset = offset;
			}
			if (count == 2) {
				secondOffset = offset;
			}
			return true;
		}
	}

	public static void applyToFunction(Program program, Function func, TaskMonitor monitor)
			throws CancelledException {
		if (func == null || func.hasCustomVariableStorage()) {
			return;
		}
		String current = func.getCallingConventionName();
		String compilerDefault = program.getCompilerSpec().getDefaultCallingConvention().getName();
		// The effective type is a pointer once forced-indirect storage is active.
		// Classify the declared aggregate, or signature events oscillate models.
		boolean gccIndirect = usesOldGcc(program) &&
			needsGccIndirectReturn(func.getReturn().getFormalDataType());
		boolean managed = current != null && current.startsWith(GCC_INDIRECT_CONVENTION_PREFIX);
		if (!managed && !gccIndirect) {
			return;
		}
		if (!managed && current != null && !current.isEmpty() &&
			!Function.DEFAULT_CALLING_CONVENTION_STRING.equals(current) &&
			!Function.UNKNOWN_CALLING_CONVENTION_STRING.equals(current) &&
			!compilerDefault.equals(current)) {
			return;
		}
		String desired = gccIndirect ? GCC_INDIRECT_CONVENTION_PREFIX + "_" +
			program.getCompilerSpec().getCompilerSpecID().toString() : compilerDefault;
		if (gccIndirect && program.getCompilerSpec().getCallingConvention(desired) == null) {
			try {
				ensureConventionInstalled(program, desired, monitor);
			}
			catch (CancelledException e) {
				throw e;
			}
			catch (Exception e) {
				throw new AssertException("Cannot install GCC aggregate return model " + desired, e);
			}
		}
		if (desired.equals(current)) {
			return;
		}
		try {
			func.setCallingConvention(desired);
		}
		catch (InvalidInputException e) {
			throw new AssertException(
				"Cannot apply " + desired + " to " + func.getEntryPoint(), e);
		}
	}
}
