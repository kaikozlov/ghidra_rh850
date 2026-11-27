//@category Verification
/* Score explicitly named function pairs already committed to a BSim database.
 *
 * Arguments: DATABASE_URL INPUT_CSV OUTPUT_JSONL
 * CSV columns:
 * label,truth,bucket,source_md5,source_name,source_address,target_md5,target_name,
 * target_address,source_instructions,target_instructions,note
 */
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import ghidra.app.script.GhidraScript;
import ghidra.features.bsim.query.BSimClientFactory;
import ghidra.features.bsim.query.FunctionDatabase;
import ghidra.features.bsim.query.description.DescriptionManager;
import ghidra.features.bsim.query.description.ExecutableRecord;
import ghidra.features.bsim.query.description.FunctionDescription;
import ghidra.features.bsim.query.protocol.ExeSpecifier;
import ghidra.features.bsim.query.protocol.FunctionEntry;
import ghidra.features.bsim.query.protocol.PairInput;
import ghidra.features.bsim.query.protocol.PairNote;
import ghidra.features.bsim.query.protocol.QueryPair;
import ghidra.features.bsim.query.protocol.ResponsePair;

public class QueryBSimPairs extends GhidraScript {
	private record Row(String label, String truth, String bucket, String sourceMd5,
		String sourceName, long sourceAddress, String targetMd5, String targetName,
		long targetAddress, int sourceInstructions, int targetInstructions,
		String note) {}

	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length != 3) {
			throw new IllegalArgumentException("usage: DATABASE_URL INPUT_CSV OUTPUT_JSONL");
		}
		Path input = Path.of(args[1]).toAbsolutePath();
		Path output = Path.of(args[2]).toAbsolutePath();
		List<Row> rows = readRows(input);
		QueryPair query = new QueryPair();
		query.pairs = new ArrayList<>();
		for (Row row : rows) {
			query.pairs.add(makePair(row));
		}

		URL url = BSimClientFactory.deriveBSimURL(args[0]);
		try (FunctionDatabase database = BSimClientFactory.buildClient(url, false)) {
			if (!database.initialize()) {
				throw new IllegalStateException(database.getLastError().message);
			}
			ResponsePair response = query.execute(database);
			if (response == null) {
				throw new IllegalStateException(database.getLastError().message);
			}
			if (response.notes.size() != rows.size()) {
				throw new IllegalStateException("pair response count " + response.notes.size() +
					" != input count " + rows.size() + "; missed exe=" + response.missedExe +
					" func=" + response.missedFunc + " vector=" + response.missedVector);
			}
			writeRows(output, rows, response.notes);
		}
		printf("BSIM pairs: %d -> %s%n", rows.size(), output);
	}

	private List<Row> readRows(Path input) throws Exception {
		List<Row> rows = new ArrayList<>();
		try (BufferedReader reader = Files.newBufferedReader(input, StandardCharsets.UTF_8)) {
			String line = reader.readLine();
			if (line == null || !line.startsWith("label,")) {
				throw new IllegalArgumentException("missing pair CSV header");
			}
			while ((line = reader.readLine()) != null) {
				if (line.isBlank()) {
					continue;
				}
				String[] fields = line.split(",", -1);
				if (fields.length != 12) {
					throw new IllegalArgumentException("expected 12 fields: " + line);
				}
				rows.add(new Row(fields[0], fields[1], fields[2], fields[3], fields[4],
					Long.decode(fields[5]), fields[6], fields[7], Long.decode(fields[8]),
					Integer.parseInt(fields[9]), Integer.parseInt(fields[10]), fields[11]));
			}
		}
		return rows;
	}

	private PairInput makePair(Row row) throws Exception {
		DescriptionManager manager = new DescriptionManager();
		ExecutableRecord sourceExe = manager.newExecutableRecord(row.sourceMd5(), "executable",
			"v850e3:LE:32:default", "default", null, null, null, null);
		ExecutableRecord targetExe = sourceExe;
		if (!row.sourceMd5().equals(row.targetMd5())) {
			targetExe = manager.newExecutableRecord(row.targetMd5(), "executable",
				"v850e3:LE:32:default", "default", null, null, null, null);
		}
		FunctionDescription source =
			manager.newFunctionDescription(row.sourceName(), row.sourceAddress(), sourceExe);
		FunctionDescription target =
			manager.newFunctionDescription(row.targetName(), row.targetAddress(), targetExe);
		PairInput pair = new PairInput();
		pair.execA = specifier(row.sourceMd5());
		pair.funcA = new FunctionEntry(source);
		pair.execB = specifier(row.targetMd5());
		pair.funcB = new FunctionEntry(target);
		return pair;
	}

	private ExeSpecifier specifier(String md5) {
		ExeSpecifier specifier = new ExeSpecifier();
		specifier.exemd5 = md5;
		return specifier;
	}

	private void writeRows(Path output, List<Row> rows, List<PairNote> notes) throws Exception {
		if (output.getParent() != null) {
			Files.createDirectories(output.getParent());
		}
		Gson gson = new Gson();
		try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
			for (int index = 0; index < rows.size(); index++) {
				Row row = rows.get(index);
				PairNote pair = notes.get(index);
				JsonObject object = new JsonObject();
				object.addProperty("label", row.label());
				object.addProperty("truth", row.truth());
				object.addProperty("bucket", row.bucket());
				object.addProperty("source_md5", row.sourceMd5());
				object.addProperty("source_address", String.format("0x%08X", row.sourceAddress()));
				object.addProperty("target_md5", row.targetMd5());
				object.addProperty("target_address", String.format("0x%08X", row.targetAddress()));
				object.addProperty("source_instructions", row.sourceInstructions());
				object.addProperty("target_instructions", row.targetInstructions());
				object.addProperty("similarity", pair.getSimilarity());
				object.addProperty("confidence", pair.getSignificance());
				object.addProperty("source_hash_count", pair.getFunc1HashCount());
				object.addProperty("target_hash_count", pair.getFunc2HashCount());
				object.addProperty("intersection_count", pair.getIntersectionCount());
				object.addProperty("note", row.note());
				writer.write(gson.toJson(object));
				writer.newLine();
			}
		}
	}
}
