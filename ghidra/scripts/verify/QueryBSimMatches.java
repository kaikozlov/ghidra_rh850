//@category Verification
/* Query every BSim-signable function in the current program against named
 * database scopes and export one best match (or an explicit miss) per scope.
 *
 * Arguments:
 *   DATABASE_URL OUTPUT_JSONL SIMILARITY CONFIDENCE MAX_MATCHES
 *   LABEL=md5:HASH|LABEL=path:PROJECT_PATH_PREFIX ...
 */
import java.io.BufferedWriter;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import ghidra.app.script.GhidraScript;
import ghidra.features.bsim.gui.filters.Md5BSimFilterType;
import ghidra.features.bsim.gui.filters.PathStartsBSimFilterType;
import ghidra.features.bsim.query.BSimClientFactory;
import ghidra.features.bsim.query.FunctionDatabase;
import ghidra.features.bsim.query.GenSignatures;
import ghidra.features.bsim.query.description.DescriptionManager;
import ghidra.features.bsim.query.description.ExecutableRecord;
import ghidra.features.bsim.query.description.FunctionDescription;
import ghidra.features.bsim.query.protocol.BSimFilter;
import ghidra.features.bsim.query.protocol.QueryNearest;
import ghidra.features.bsim.query.protocol.ResponseNearest;
import ghidra.features.bsim.query.protocol.SimilarityNote;
import ghidra.program.model.listing.Function;
import ghidra.features.bsim.query.protocol.SimilarityResult;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.InstructionIterator;

public class QueryBSimMatches extends GhidraScript {
	private record Scope(String label, String kind, String value) {}

	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		if (currentProgram == null || args.length < 6) {
			throw new IllegalArgumentException(
				"usage: DATABASE_URL OUTPUT_JSONL SIMILARITY CONFIDENCE MAX_MATCHES " +
				"LABEL=md5:HASH|LABEL=path:PREFIX ...");
		}
		String databaseUrl = args[0];
		Path output = Path.of(args[1]).toAbsolutePath();
		double similarity = Double.parseDouble(args[2]);
		double confidence = Double.parseDouble(args[3]);
		int maxMatches = Integer.parseInt(args[4]);
		if (similarity < 0.0 || similarity > 1.0 || confidence < 0.0 || maxMatches < 1) {
			throw new IllegalArgumentException("invalid BSim thresholds or match bound");
		}
		List<Scope> scopes = new ArrayList<>(args.length - 5);
		for (int i = 5; i < args.length; i++) {
			scopes.add(parseScope(args[i]));
		}
		if (output.getParent() != null) {
			Files.createDirectories(output.getParent());
		}

		URL url = BSimClientFactory.deriveBSimURL(databaseUrl);
		try (FunctionDatabase database = BSimClientFactory.buildClient(url, false)) {
			if (!database.initialize()) {
				throw new IllegalStateException(database.getLastError().message);
			}
			GenSignatures signatures = new GenSignatures(false);
			try {
				signatures.setVectorFactory(database.getLSHVectorFactory());
				signatures.openProgram(currentProgram, null, null, null, null, null);
				FunctionIterator functions = currentProgram.getFunctionManager().getFunctionsNoStubs(true);
				signatures.scanFunctions(functions,
					currentProgram.getFunctionManager().getFunctionCount(), monitor);
				DescriptionManager manager = signatures.getDescriptionManager();
				List<FunctionDescription> sources = new ArrayList<>();
				manager.listAllFunctions().forEachRemaining(sources::add);
				writeQueries(database, manager, sources, scopes, output, databaseUrl,
					similarity, confidence, maxMatches);
				printf("BSIM query: %d signable functions x %d scopes -> %s%n",
					sources.size(), scopes.size(), output);
			}
			finally {
				signatures.dispose();
			}
		}
	}

	private Scope parseScope(String raw) {
		int equals = raw.indexOf('=');
		int colon = raw.indexOf(':', equals + 1);
		if (equals <= 0 || colon <= equals + 1 || colon == raw.length() - 1) {
			throw new IllegalArgumentException("invalid scope: " + raw);
		}
		String kind = raw.substring(equals + 1, colon);
		if (!kind.equals("md5") && !kind.equals("path")) {
			throw new IllegalArgumentException("invalid scope kind: " + kind);
		}
		return new Scope(raw.substring(0, equals), kind, raw.substring(colon + 1));
	}

	private void writeQueries(FunctionDatabase database, DescriptionManager manager,
			List<FunctionDescription> sources, List<Scope> scopes, Path output,
			String databaseUrl, double similarity, double confidence, int maxMatches)
			throws Exception {
		Gson gson = new Gson();
		try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
			JsonObject metadata = new JsonObject();
			metadata.addProperty("record", "metadata");
			metadata.addProperty("schema", "rh850-bsim-query-v1");
			metadata.addProperty("program", currentProgram.getName());
			metadata.addProperty("md5", currentProgram.getExecutableMD5());
			metadata.addProperty("database", databaseUrl);
			metadata.addProperty("similarity_threshold", similarity);
			metadata.addProperty("confidence_threshold", confidence);
			metadata.addProperty("max_matches", maxMatches);
			metadata.addProperty("source_function_count", sources.size());
			metadata.addProperty("scope_count", scopes.size());
			writeJsonLine(writer, gson, metadata);

			for (Scope scope : scopes) {
				monitor.checkCancelled();
				Map<Long, SimilarityNote> best = queryScope(database, manager, scope,
					similarity, confidence, maxMatches);
				for (FunctionDescription source : sources) {
					JsonObject row = new JsonObject();
					row.addProperty("record", "match");
					row.addProperty("scope", scope.label());
					row.addProperty("source_address", String.format("0x%08X", source.getAddress()));
					row.addProperty("source_name", source.getFunctionName());
					Function sourceFunction = currentProgram.getFunctionManager().getFunctionAt(
						currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(
							source.getAddress()));
					row.addProperty("source_instruction_count",
						countInstructions(sourceFunction));
					SimilarityNote note = best.get(source.getAddress());
					row.addProperty("matched", note != null);
					if (note != null) {
						FunctionDescription target = note.getFunctionDescription();
						ExecutableRecord executable = target.getExecutableRecord();
						row.addProperty("similarity", note.getSimilarity());
						row.addProperty("confidence", note.getSignificance());
						row.addProperty("target_address",
							String.format("0x%08X", target.getAddress()));
						row.addProperty("target_name", target.getFunctionName());
						row.addProperty("target_executable", executable.getNameExec());
						row.addProperty("target_md5", executable.getMd5());
						row.addProperty("target_path", executable.getPath());
						row.addProperty("target_architecture", executable.getArchitecture());
						row.addProperty("target_compiler", executable.getNameCompiler());
					}
					writeJsonLine(writer, gson, row);
				}
			}
		}
	}

	private Map<Long, SimilarityNote> queryScope(FunctionDatabase database,
			DescriptionManager manager, Scope scope, double similarity, double confidence,
			int maxMatches) throws Exception {
		QueryNearest query = new QueryNearest();
		query.manage = manager;
		query.max = maxMatches;
		query.thresh = similarity;
		query.signifthresh = confidence;
		query.bsimFilter = new BSimFilter();
		if (scope.kind().equals("md5")) {
			query.bsimFilter.addAtom(new Md5BSimFilterType(), scope.value());
		}
		else {
			query.bsimFilter.addAtom(new PathStartsBSimFilterType(), scope.value());
		}
		ResponseNearest response = query.execute(database);
		if (response == null) {
			throw new IllegalStateException(database.getLastError().message);
		}
		Map<Long, SimilarityNote> best = new HashMap<>();
		Iterator<SimilarityResult> results = response.result.iterator();
		while (results.hasNext()) {
			SimilarityResult result = results.next();
			long address = result.getBase().getAddress();
			for (SimilarityNote note : result) {
				SimilarityNote previous = best.get(address);
				if (previous == null || note.getSimilarity() > previous.getSimilarity() ||
					(note.getSimilarity() == previous.getSimilarity() &&
						note.getSignificance() > previous.getSignificance())) {
					best.put(address, note);
				}
			}
		}
		return best;
	}

	private int countInstructions(Function function) {
		if (function == null) {
			return 0;
		}
		int count = 0;
		InstructionIterator instructions =
			currentProgram.getListing().getInstructions(function.getBody(), true);
		while (instructions.hasNext()) {
			instructions.next();
			count++;
		}
		return count;
	}

	private void writeJsonLine(BufferedWriter writer, Gson gson, JsonObject object)
			throws Exception {
		writer.write(gson.toJson(object));
		writer.newLine();
	}
}
