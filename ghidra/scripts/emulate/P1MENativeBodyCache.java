import java.io.IOException;
import java.lang.foreign.Arena;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.SymbolLookup;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/** The compiler worker receives only immutable C source and a body identity, never a site. */
final class P1MENativeBodyCache {
    private static final String FORMAT = "body-v2";
    static final int MAX_SHAPES = 4096;
    private static final int MAX_BATCH = 48;
    private static final long COALESCE_NS = TimeUnit.MILLISECONDS.toNanos(10);
    private static final long COMPILE_NS = TimeUnit.SECONDS.toNanos(20);
    private static final int MAX_ATTEMPTS_PER_BATCH = 12;
    private static final int MAX_EMPTY_BUILDS = 3;
    private static final int MAX_DIAGNOSTICS = 8, MAX_DETAIL = 1000;
    private static final String BODY_SIGNATURE =
        "(struct ctx *restrict ctx,uint64_t *restrict a,uint8_t *restrict p0,uint8_t *restrict p1){\n";
    private static final byte[] BODY_SIGNATURE_BYTES = BODY_SIGNATURE.getBytes(StandardCharsets.US_ASCII);

    static final class Body {
        final String name;
        volatile MemorySegment function;

        Body(String name) {
            this.name = name;
        }
    }

    private record Job(Body body, String code) {}
    private record Image(Arena arena, SymbolLookup symbols) {}
    private record Host(String directory, String suffix, String sharedFlag) {
        static Host current() {
            String os = System.getProperty("os.name").toLowerCase(Locale.ROOT);
            String arch = System.getProperty("os.arch").toLowerCase(Locale.ROOT);
            if (ByteOrder.nativeOrder() != ByteOrder.LITTLE_ENDIAN ||
                    java.lang.foreign.ValueLayout.ADDRESS.byteSize() != Long.BYTES)
                throw new UnsupportedOperationException("native window graph requires 64-bit little-endian pointers");
            arch = switch (arch) {
                case "arm64" -> "aarch64";
                case "amd64" -> "x86_64";
                default -> arch;
            };
            if (os.equals("mac os x") || os.equals("darwin")) return new Host("darwin-" + arch, ".dylib", "-dynamiclib");
            if (os.equals("linux")) return new Host("linux-" + arch, ".so", "-shared");
            throw new UnsupportedOperationException("no native window graph compiler recipe for " + os);
        }
    }

    private final Host host;
    private final Path root, directory;
    private final String abi, runnerId, header, compiler;
    private final Map<String, Body> bodies = new HashMap<>();
    private final ArrayDeque<Job> pending = new ArrayDeque<>();
    private final ArrayDeque<String> diagnostics = new ArrayDeque<>();
    private final Map<String, MemorySegment> installed = new HashMap<>();
    private final List<Image> images = new ArrayList<>();
    private boolean running, stopped, limitReported;
    private long failureCount;
    private long built;
    private volatile boolean closing, compilerDisabled;
    private volatile Process activeCompiler;
    private int emptyBuilds;

    P1MENativeBodyCache(Path sources, Path cache, String compiler) throws IOException {
        this.host = Host.current();
        byte[] abiHeader = Files.readAllBytes(sources.resolve("windowgraph-abi.h"));
        byte[] runner = Files.readAllBytes(sources.resolve("windowgraph-runner.c"));
        abi = sha256(abiHeader);
        runnerId = sha256(abiHeader, runner);
        header = new String(abiHeader, StandardCharsets.UTF_8);
        root = cache.toAbsolutePath();
        directory = root.resolve(host.directory).resolve(FORMAT + "-" + abi);
        this.compiler = compiler;
    }

    SymbolLookup openRunner() {
        return openRunner(root);
    }

    SymbolLookup openRunner(Path runnerCache) {
        var runner = SymbolLookup.libraryLookup(runnerCache.toAbsolutePath().resolve(host.directory)
            .resolve("runner-" + runnerId + host.suffix), Arena.ofAuto());
        requireAbi(runner, runnerId);
        restoreCatalog();
        return runner;
    }

    void installShutdownHook() {
        Runtime.getRuntime().addShutdownHook(Thread.ofPlatform().name("p1me-native-compiler-stop")
            .inheritInheritableThreadLocals(false).unstarted(() -> {
                closing = true;
                Process process = activeCompiler;
                if (process != null) kill(process);
            }));
    }

    private static void requireAbi(SymbolLookup symbols, String abi) {
        if (symbols.find("wg_abi_" + abi).isEmpty()) throw new IllegalArgumentException("native window graph ABI mismatch");
    }

    static String sha256(byte[]... parts) {
        try {
            var digest = MessageDigest.getInstance("SHA-256");
            for (byte[] part : parts) digest.update(part);
            return HexFormat.of().formatHex(digest.digest());
        }
        catch (NoSuchAlgorithmException e) {
            throw new AssertionError(e);
        }
    }

    synchronized Body request(String code) {
        String name = "p_" + sha256(BODY_SIGNATURE_BYTES, code.getBytes(StandardCharsets.UTF_8));
        Body previous = bodies.get(name);
        if (previous != null) return previous;
        if (stopped || closing) return null;
        if (bodies.size() >= MAX_SHAPES) {
            if (!limitReported) failure("queue", "process shape limit of " + MAX_SHAPES + " reached");
            limitReported = true;
            return null;
        }
        Body body = new Body(name);
        bodies.put(name, body);
        body.function = installed.remove(name);
        if (body.function != null) return body;
        if (compilerDisabled) return body;
        pending.addLast(new Job(body, code));
        if (!running) {
            running = true;
            try {
                Thread.ofVirtual().name("p1me-native-compiler").inheritInheritableThreadLocals(false).start(this::drain);
            }
            catch (RuntimeException | LinkageError e) {
                stop(e);
                return null;
            }
        }
        else notifyAll();
        return body;
    }

    synchronized void failure(String stage, String detail) {
        failureCount++;
        if (diagnostics.size() == MAX_DIAGNOSTICS) return;
        diagnostics.add(bounded(stage + ": " + detail));
    }

    static String bounded(String detail) {
        return detail.substring(0, Math.min(detail.length(), MAX_DETAIL)).replace('\n', ' ').replace('\r', ' ');
    }

    synchronized String diagnostic() {
        return "compiler-disabled=" + compilerDisabled + ", failures=" + failureCount +
            ", first-failures=" + diagnostics;
    }

    private synchronized void stop(Throwable error) {
        failure("worker", error.toString());
        stopped = true;
        running = false;
        pending.clear();
    }

    private synchronized Job take(long until) throws InterruptedException {
        long left;
        while (pending.isEmpty() && !closing && (left = until - System.nanoTime()) > 0)
            TimeUnit.NANOSECONDS.timedWait(this, left);
        return closing ? null : pending.pollFirst();
    }

    private void drain() {
        try {
            while (!closing) {
                Job first;
                synchronized (this) {
                    first = pending.pollFirst();
                    if (first == null) {
                        running = false;
                        return;
                    }
                }
                var misses = new ArrayList<Job>(MAX_BATCH);
                long until = System.nanoTime() + COALESCE_NS;
                Job job = first;
                for (int i = 1;; i++) {
                    misses.add(job);
                    if (i == MAX_BATCH || (job = take(compilerDisabled ? System.nanoTime() : until)) == null)
                        break;
                }
                if (!misses.isEmpty() && !compilerDisabled && !closing) {
                    long previous = built;
                    misses.sort(Comparator.comparing(jobToBuild -> jobToBuild.body.name));
                    compile(misses, new BuildBudget());
                    emptyBuilds = built != previous ? 0 : emptyBuilds + 1;
                    if (!compilerDisabled && emptyBuilds == MAX_EMPTY_BUILDS) {
                        failure("compiler", "disabled after " + emptyBuilds + " unsuccessful batches");
                        compilerDisabled = true;
                    }
                }
            }
        }
        catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            stop(e);
        }
        catch (RuntimeException | LinkageError e) {
            stop(e);
        }
    }

    private Path imagePath(String id) {
        return directory.resolve(id + host.suffix);
    }

    private void restoreCatalog() {
        if (!Files.isDirectory(directory)) return;
        try (var entries = Files.newDirectoryStream(directory, "*.names")) {
            for (Path catalog : entries) {
                if (installed.size() >= MAX_SHAPES) break;
                try {
                    String file = catalog.getFileName().toString();
                    String id = file.substring(0, file.length() - ".names".length());
                    if (!validImageId(id)) continue;
                    byte[] encoded;
                    try (var in = Files.newInputStream(catalog)) {
                        encoded = in.readNBytes(MAX_BATCH * 66 + 1);
                    }
                    if (encoded.length == 0 || encoded.length > MAX_BATCH * 66 || encoded.length % 66 != 0 ||
                            !sha256(encoded).equals(id)) throw new IOException("invalid native body catalog");
                    String names = new String(encoded, StandardCharsets.US_ASCII);
                    boolean loaded = false;
                    Image image = load(imagePath(id));
                    try {
                        for (int i = 0; i < names.length() && installed.size() < MAX_SHAPES; i += 66) {
                            String name = names.substring(i, i + 66);
                            if (installed.containsKey(name)) continue;
                            var fn = image.symbols.find(name).orElseThrow(() -> new IOException("missing body " + name));
                            if (!loaded) { images.add(image); loaded = true; }
                            installed.put(name, fn);
                        }
                    }
                    finally { if (!loaded) image.arena.close(); }
                }
                catch (IOException | RuntimeException | LinkageError e) { failure("cache catalog", e.toString()); }
            }
        }
        catch (IOException | RuntimeException e) { failure("cache catalog directory", e.toString()); }
    }

    private static boolean validImageId(String id) {
        if (id.length() != 64) return false;
        for (int i = 0; i < id.length(); i++) {
            char c = id.charAt(i);
            if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f')) return false;
        }
        return true;
    }

    private Image load(Path path) {
        Arena arena = Arena.ofShared();
        try {
            SymbolLookup symbols = SymbolLookup.libraryLookup(path, arena);
            requireAbi(symbols, abi);
            return new Image(arena, symbols);
        }
        catch (RuntimeException | LinkageError e) {
            arena.close();
            throw e;
        }
    }

    private static final class BuildBudget {
        final long until = System.nanoTime() + COMPILE_NS;
        int remaining = MAX_ATTEMPTS_PER_BATCH;
    }

    private void compile(List<Job> jobs, BuildBudget budget) throws InterruptedException {
        if (closing || compilerDisabled || budget.remaining-- <= 0 || budget.until - System.nanoTime() <= 0) return;
        Path temporary = null;
        boolean split = false;
        try {
            Files.createDirectories(directory);
            temporary = Files.createTempDirectory(directory, ".compile-");
            Path input = temporary.resolve("body.c"), log = temporary.resolve("compiler.log");
            Path artifact = temporary.resolve("body" + host.suffix);
            var names = new StringBuilder(jobs.size() * 66);
            try (var writer = Files.newBufferedWriter(input)) {
                writer.write(header);
                writer.write("\nint wg_abi_" + abi + "(void) { return 0; }\n");
                for (Job job : jobs) {
                    names.append(job.body.name);
                    writer.write("int " + job.body.name + BODY_SIGNATURE);
                    writer.write(job.code);
                    writer.write("}\n");
                }
            }
            Process process;
            try {
                process = new ProcessBuilder(compiler, "-std=c11", "-O3", "-fPIC", host.sharedFlag,
                    "-o", artifact.toString(), input.toString()).redirectErrorStream(true)
                    .redirectOutput(log.toFile()).start();
            }
            catch (IOException | SecurityException e) {
                failure("start compiler " + compiler, e.toString());
                compilerDisabled = true;
                return;
            }
            activeCompiler = process;
            try {
                if (closing || !process.waitFor(Math.max(0, budget.until - System.nanoTime()), TimeUnit.NANOSECONDS)) {
                    if (!closing) failure("compiler " + compiler, "batch deadline exceeded");
                    compilerDisabled = true;
                    return;
                }
                if (process.exitValue() == 0) {
                    String id = sha256(names.toString().getBytes(StandardCharsets.US_ASCII));
                    publish(jobs, id, names, artifact);
                    return;
                }
                try (var stream = Files.newInputStream(log)) {
                    failure("compiler exit " + process.exitValue() + " (" + jobs.size() + " bodies, first " +
                        jobs.getFirst().body.name + ")", new String(stream.readNBytes(MAX_DETAIL), StandardCharsets.UTF_8));
                }
                split = jobs.size() > 1;
            }
            finally {
                if (process.isAlive()) kill(process);
                activeCompiler = null;
            }
        }
        catch (IOException | RuntimeException | LinkageError e) {
            failure("build native bodies", e.toString());
        }
        finally {
            if (temporary != null) {
                try (var paths = Files.list(temporary)) {
                    for (Path file : paths.toList()) Files.deleteIfExists(file);
                    Files.deleteIfExists(temporary);
                }
                catch (IOException | RuntimeException e) {
                    failure("compiler cleanup", e.toString());
                }
            }
        }
        if (split) {
            int middle = jobs.size() / 2;
            compile(jobs.subList(0, middle), budget);
            compile(jobs.subList(middle, jobs.size()), budget);
        }
    }

    private void publish(List<Job> jobs, String id, CharSequence names, Path artifact) throws IOException {
        Image image = load(artifact);
        boolean installed = false;
        try {
            var functions = new MemorySegment[jobs.size()];
            for (int i = 0; i < jobs.size(); i++) {
                String name = jobs.get(i).body.name;
                functions[i] = image.symbols.find(name)
                    .orElseThrow(() -> new IllegalArgumentException("compiler output did not export " + name));
            }
            atomicMove(artifact, imagePath(id));
            images.add(image);
            installed = true;
            for (int i = 0; i < jobs.size(); i++) jobs.get(i).body.function = functions[i];
            Path catalog = artifact.resolveSibling("body.names");
            Files.writeString(catalog, names, StandardCharsets.US_ASCII);
            atomicMove(catalog, directory.resolve(id + ".names"));
            built += jobs.size();
        }
        finally {
            if (!installed) image.arena.close();
        }
    }

    private static void atomicMove(Path from, Path to) throws IOException {
        Files.move(from, to, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
    }

    private static void kill(Process process) {
        process.descendants().forEach(ProcessHandle::destroyForcibly);
        process.destroyForcibly();
    }
}
