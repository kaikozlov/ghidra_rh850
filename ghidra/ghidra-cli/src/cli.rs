use clap::error::{ContextKind, ContextValue, ErrorKind};
use clap::{ArgAction, Args, Parser, Subcommand};
use serde::{Deserialize, Serialize};

#[derive(Parser)]
#[command(name = "ghidra")]
#[command(
    version,
    about = "Inspect functions, list program data, and navigate cross-references",
    long_about = "Inspect functions, list program data, and navigate cross-references.\n\nUse --json for machine-readable output or --pretty for indented JSON. List commands show 50 rows by default. Set --limit 0 to show every row.",
    after_help = "Examples:\n  ghidra inspect main\n  ghidra function list --filter 'name^init' --fields address,name\n  ghidra disasm main -n 20\n  ghidra query imports --json"
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,

    /// Increase log verbosity printed to stderr (-v=warn, -vv=info, -vvv=debug)
    #[arg(short, long, action = ArgAction::Count, global = true)]
    pub verbose: u8,

    /// Suppress non-essential output
    #[arg(short, long, global = true)]
    pub quiet: bool,

    /// Print compact JSON
    #[arg(long, global = true)]
    pub json: bool,

    /// Print indented JSON
    #[arg(long, global = true)]
    pub pretty: bool,

    /// Project name or path (can also be specified per-subcommand)
    #[arg(long, global = true)]
    pub project: Option<String>,

    /// Program name within the project (can also be specified per-subcommand)
    #[arg(long, global = true)]
    pub program: Option<String>,

    /// Directory under which Ghidra projects are stored.
    /// Overrides config `ghidra_project_dir` and the default location.
    /// Note: Ghidra 12.1+ rejects paths containing a dot-prefixed component.
    #[arg(long, global = true)]
    pub projects_dir: Option<std::path::PathBuf>,

    /// Full JDK home for Ghidra to use (must be a JDK, not a JRE).
    /// Overrides config `java_home` and auto-detection.
    #[arg(long, global = true)]
    pub java_home: Option<std::path::PathBuf>,
}

impl Cli {
    pub(crate) fn parse_invocation() -> Self {
        Self::try_parse().unwrap_or_else(|mut error| {
            add_invocation_hints(&mut error);
            error.exit()
        })
    }
}

fn add_invocation_hints(error: &mut clap::Error) {
    let (invalid, insertions): (ContextKind, &[&str]) = match error.kind() {
        ErrorKind::UnknownArgument => (ContextKind::InvalidArg, &["-n"]),
        ErrorKind::InvalidSubcommand => (ContextKind::InvalidSubcommand, &["to", "from"]),
        _ => return,
    };
    let Some(ContextValue::String(token)) = error.get(invalid) else {
        return;
    };
    if invalid == ContextKind::InvalidArg && token.parse::<usize>().is_err() {
        return;
    }

    let Some(args) = std::env::args_os()
        .map(|arg| {
            arg.into_string()
                .ok()
                .filter(|arg| !arg.contains(char::is_control))
        })
        .collect::<Option<Vec<_>>>()
    else {
        return;
    };
    // Reparse each repair to check the command and preserve argument boundaries.
    let mut corrected: Vec<_> = args.iter().map(String::as_str).collect();
    for (index, arg) in args.iter().enumerate().skip(1).rev() {
        if arg != token {
            continue;
        }
        let mut repairs = Vec::new();
        for &insertion in insertions {
            if insertion == "-n" && index > 1 && args[index - 1] == "--count" {
                corrected[index - 1] = insertion;
                let repair = invocation_hint(&corrected, insertion);
                corrected[index - 1] = "--count";
                if let Some(repair) = repair {
                    repairs.push(repair);
                    break;
                }
            }
            corrected.insert(index, insertion);
            repairs.extend(invocation_hint(&corrected, insertion));
            corrected.remove(index);
        }
        if repairs.len() == insertions.len() {
            if let Some(ContextValue::StyledStrs(mut tips)) = error.remove(ContextKind::Suggested) {
                tips.append(&mut repairs);
                repairs = tips;
            }
            error.insert(ContextKind::Suggested, ContextValue::StyledStrs(repairs));
            return;
        }
    }
}

fn invocation_hint(args: &[&str], insertion: &str) -> Option<clap::builder::StyledStr> {
    let cli = Cli::try_parse_from(args.iter().copied()).ok()?;
    if !matches!(
        (insertion, cli.command),
        ("-n", Commands::Disasm(_))
            | ("to", Commands::XRef(XRefCommands::To(_)))
            | ("from", Commands::XRef(XRefCommands::From(_)))
    ) {
        return None;
    }
    let command = shlex::try_join(args.iter().copied()).ok()?;
    Some(format!("try: {command}").into())
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum Commands {
    /// List functions, strings, imports, exports, or memory blocks
    #[command(
        display_order = 4,
        after_help = "Examples:\n  ghidra query functions --count\n  ghidra query strings --filter 'value~error' --fields address,value\n  ghidra query imports --json"
    )]
    Query(QueryArgs),

    /// Project management commands
    #[command(display_order = 70)]
    Project(ProjectArgs),

    /// Program/binary management commands
    #[command(subcommand, display_order = 71, alias = "prog", alias = "programs")]
    Program(ProgramCommands),

    /// List, inspect, or edit functions
    #[command(
        subcommand,
        display_order = 3,
        alias = "fn",
        alias = "func",
        alias = "functions"
    )]
    Function(FunctionCommands),

    /// List defined strings or show references to a string
    #[command(subcommand, display_order = 6, alias = "string", alias = "str")]
    Strings(StringsCommands),

    /// List, inspect, or edit symbols
    #[command(subcommand, display_order = 12, alias = "sym", alias = "symbols")]
    Symbol(SymbolCommands),

    /// Show memory blocks, read bytes, or search for a byte pattern
    #[command(subcommand, display_order = 11, alias = "mem")]
    Memory(MemoryCommands),

    /// List references to or from an address or symbol
    #[command(
        subcommand,
        display_order = 7,
        alias = "xrefs",
        alias = "xref",
        alias = "crossref",
        alias = "crossrefs"
    )]
    XRef(XRefCommands),

    /// Type operations
    #[command(subcommand, display_order = 13, alias = "types")]
    Type(TypeCommands),

    /// Comment operations
    #[command(subcommand, display_order = 14, alias = "comments")]
    Comment(CommentCommands),

    /// Search for functions, strings, byte patterns, or calls
    #[command(subcommand, display_order = 8, alias = "search")]
    Find(FindCommands),

    /// Graph operations
    #[command(subcommand, alias = "callgraph", alias = "cg")]
    Graph(GraphCommands),

    /// Decompile the function at a name or address
    #[command(
        alias = "decomp",
        alias = "dec",
        display_order = 1,
        after_help = "Examples:\n  ghidra decompile main -o c\n  ghidra decompile main --with-vars --with-params --pretty"
    )]
    Decompile(DecompileArgs),

    /// Show instructions starting at a name or address
    #[command(
        alias = "disassemble",
        alias = "dis",
        display_order = 2,
        after_help = "Examples:\n  ghidra disasm main -n 20\n  ghidra disasm 0x401000 -n 40 -o asm\n  ghidra disasm main --json"
    )]
    Disasm(DisasmArgs),

    /// Diff operations
    #[command(subcommand)]
    Diff(DiffCommands),

    /// Dump/export data
    #[command(subcommand, alias = "export")]
    Dump(DumpCommands),

    /// Patch binary
    #[command(subcommand)]
    Patch(PatchCommands),

    /// Script execution
    #[command(subcommand, alias = "scripts")]
    Script(ScriptCommands),

    /// Execute commands from a file or stdin
    #[command(display_order = 9)]
    Batch(BatchArgs),

    /// Configuration management
    #[command(subcommand)]
    Config(ConfigCommands),

    /// Set default values
    SetDefault(SetDefaultArgs),

    /// Show program metadata, address range, and function count
    #[command(alias = "info", display_order = 5)]
    Summary(SummaryArgs),

    /// Count functions, symbols, instructions, and other program data
    #[command(display_order = 10)]
    Stats(StatsArgs),

    /// Show version information
    Version,

    /// Check Ghidra installation
    Doctor,

    /// Initialize configuration
    Init,

    /// Import a binary into a project
    Import(ImportArgs),

    /// Analyze a program
    #[command(alias = "analysis")]
    Analyze(AnalyzeArgs),

    /// Start the bridge
    Start {
        /// Project path
        #[arg(long)]
        project: Option<String>,
        /// Program name to load
        #[arg(long)]
        program: Option<String>,
    },

    /// Stop the bridge
    Stop {
        /// Project path
        #[arg(long)]
        project: Option<String>,
        /// Compatibility flag; clean bridge teardown is already the durable save boundary
        #[arg(long)]
        save: bool,
    },

    /// Restart the bridge
    Restart {
        /// Project path
        #[arg(long)]
        project: Option<String>,
        /// Program name to load
        #[arg(long)]
        program: Option<String>,
    },

    /// Show bridge status
    Status {
        /// Project path
        #[arg(long)]
        project: Option<String>,
    },

    /// Ping the bridge
    Ping {
        /// Project path
        #[arg(long)]
        project: Option<String>,
    },

    /// List active, queued, and recently completed bridge jobs
    Jobs {
        /// Show one job by ID; omit for the bridge queue and recent jobs
        job_id: Option<u64>,
        /// Project path
        #[arg(long)]
        project: Option<String>,
    },

    /// Request cooperative cancellation of a bridge job (defaults to active job)
    Cancel {
        /// Job ID; omit to cancel the currently active job
        job_id: Option<u64>,
        /// Project path
        #[arg(long)]
        project: Option<String>,
    },

    /// Download and setup Ghidra automatically
    Setup(SetupArgs),

    /// Rename a symbol (shortcut for `symbol rename`)
    #[command(alias = "mv")]
    Rename(RenameArgs),

    /// Show a function overview or selected detail sections
    #[command(
        display_order = 0,
        long_about = "Inspect one or more functions. Compact output defaults to function metadata, callers, and callees. Non-compact formats, batch, and queries with --fields, --filter, or --sort default to every section.\n\nSelect sections explicitly or use --all. Use --disasm N to set the instruction count and --limit N to cap each call or reference list.",
        after_help = "Examples:\n  ghidra inspect main init\n  ghidra inspect main --decompile --xrefs\n  ghidra inspect main --all --disasm 20"
    )]
    Inspect(InspectArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct InspectArgs {
    /// One or more function targets (name | address | FUN_<hex>)
    #[arg(
        value_name = "TARGET",
        num_args = 1..,
        required_unless_present = "target",
        conflicts_with = "target"
    )]
    pub positional_targets: Vec<String>,
    /// Alternate form for a single target
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Include every section (40 instructions unless --disasm sets the count)
    #[arg(long)]
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub all: bool,
    /// Include decompiled C (JSON also includes parameter and local storage)
    #[arg(long)]
    pub decompile: bool,
    /// Include direct callers
    #[arg(long)]
    pub callers: bool,
    /// Include direct callees
    #[arg(long)]
    pub callees: bool,
    /// Include references to the function entry and references from its body
    #[arg(long)]
    pub xrefs: bool,
    /// Include up to N instructions from the function entry
    #[arg(long, value_name = "N")]
    pub disasm: Option<usize>,
    /// Maximum number of targets per request (at least 1)
    #[arg(long, default_value_t = 20)]
    pub max_targets: usize,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl InspectArgs {
    pub fn resolved_targets(&self) -> Vec<&str> {
        if let Some(target) = self.target.as_deref() {
            vec![target]
        } else {
            self.positional_targets.iter().map(String::as_str).collect()
        }
    }
}

const FIELDS_LONG_HELP: &str = "Select comma-separated fields (for example, --fields address,name).\nIn compact lists, use one field for one value per row or several fields for columns in that order.\nUse --fields=-comment,signature to exclude fields instead.";
const FORMAT_LONG_HELP: &str = "Text: compact, full, minimal, table, ids, count.\nStructured: json (indented), json-compact, ndjson (json-stream), csv, tsv.\nUse c with decompile, asm with disasm, or hex with memory read.\nAn explicit format takes precedence over --json and --pretty.";

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct QueryArgs {
    /// Data set: functions, strings, imports, exports, or memory
    pub data_type: String,

    /// Target program
    #[arg(long, env = "GHIDRA_DEFAULT_PROGRAM")]
    pub program: Option<String>,

    /// Project name
    #[arg(long, env = "GHIDRA_DEFAULT_PROJECT")]
    pub project: Option<String>,

    /// Filter expression: <field><op><value>, e.g. 'name~PK' (contains),
    /// 'name=~"^PK_"' (regex), 'size>100'. Ops: = != > >= < <= ~ ^ $ =~.
    /// Combine with AND/OR/NOT. Bare words are rejected.
    #[arg(short, long)]
    pub filter: Option<String>,

    /// Select comma-separated fields (use --fields=-FIELD to exclude)
    #[arg(long, long_help = FIELDS_LONG_HELP)]
    pub fields: Option<String>,

    /// Output format, e.g. compact, json, ndjson, csv, tsv, or table
    #[arg(long, short = 'o', long_help = FORMAT_LONG_HELP)]
    pub format: Option<String>,

    /// Maximum number of results (0 = unlimited; default 50)
    #[arg(long)]
    pub limit: Option<usize>,

    /// Skip first N results
    #[arg(long)]
    pub offset: Option<usize>,

    /// Sort by field(s) (comma-separated, prefix with - for descending)
    #[arg(long, allow_hyphen_values = true)]
    pub sort: Option<String>,

    /// Print only the count, with any explicit --limit and --offset
    #[arg(long)]
    pub count: bool,

    /// Print compact JSON (use --pretty for indented JSON)
    #[arg(long)]
    pub json: bool,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ProjectArgs {
    #[command(subcommand)]
    pub command: ProjectCommands,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum ProjectCommands {
    /// Create a new project
    Create { name: String },
    /// List all projects
    List,
    /// Delete a project
    Delete { name: String },
    /// Show project information
    Info { name: Option<String> },
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum ProgramCommands {
    /// List all programs in the project
    #[command(alias = "ls")]
    List(ProgramTargetArgs),
    /// Open/switch to a program
    Open(ProgramTargetArgs),
    /// Close a program
    Close(ProgramTargetArgs),
    /// Delete a program
    Delete(ProgramTargetArgs),
    /// Show program information
    Info(ProgramTargetArgs),
    /// Export program
    Export(ExportArgs),
    /// Save the current program durably (explicit persistence boundary)
    Save(ProgramSaveArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ProgramTargetArgs {
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ProgramSaveArgs {
    /// Commit message for the save (recorded in the program's change history)
    #[arg(long)]
    pub message: Option<String>,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ExportArgs {
    /// Export format (xml, json, asm, c)
    pub format: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
    /// Output file
    #[arg(short, long)]
    pub output: Option<String>,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum FunctionCommands {
    /// List functions with optional filters, sorting, and field selection
    #[command(
        alias = "ls",
        after_help = "Examples:\n  ghidra function list --filter 'name^init' --fields address,name\n  ghidra function list --sort=-size --limit 10\n  ghidra function list --fields name --limit 0"
    )]
    List(QueryOptions),
    /// Get function details
    #[command(alias = "show", alias = "detail")]
    Get(FunctionGetArgs),
    /// Decompile function
    #[command(alias = "decomp")]
    Decompile(FunctionDecompileArgs),
    /// Show instructions at the function target (use `disasm -n N` to set the count)
    #[command(alias = "disassemble", alias = "dis")]
    Disasm(FunctionGetArgs),
    /// Get function calls
    Calls(FunctionGetArgs),
    /// Get cross-references to function
    #[command(alias = "xrefs", alias = "crossrefs", alias = "references")]
    XRefs(FunctionGetArgs),
    /// Rename function
    Rename(RenameArgs),
    /// Create function
    Create(CreateFunctionArgs),
    /// Delete function
    Delete(FunctionGetArgs),
    /// Set function signature from C-style string
    SetSignature(SetSignatureArgs),
    /// Set function return type
    SetReturnType(SetReturnTypeArgs),
    /// Set function calling convention
    SetCallingConvention(SetCallingConventionArgs),
    /// Set variable type in a function
    SetVarType(SetVarTypeArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct FunctionGetArgs {
    /// Function target (name/address/FUN_...)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl FunctionGetArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct RenameArgs {
    pub old_name: String,
    pub new_name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct CreateFunctionArgs {
    pub address: String,
    pub name: Option<String>,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct FunctionDecompileArgs {
    /// Function target (name/address/FUN_...)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Include local variable details (name, type, storage)
    #[arg(long)]
    pub with_vars: bool,
    /// Include parameter details (name, type, storage)
    #[arg(long)]
    pub with_params: bool,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl FunctionDecompileArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SetSignatureArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// C-style signature string, e.g. "int main(int argc, char** argv)"
    #[arg(long)]
    pub signature: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

impl SetSignatureArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SetReturnTypeArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Return type name
    #[arg(long = "type")]
    pub return_type: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

impl SetReturnTypeArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SetCallingConventionArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Calling convention name (e.g., "__cdecl", "__stdcall", "__fastcall")
    #[arg(long)]
    pub convention: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

impl SetCallingConventionArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SetVarTypeArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Variable name to retype
    #[arg(long = "var")]
    pub var_name: String,
    /// New type name (e.g., "int", "char *", "MyStruct")
    #[arg(long = "type")]
    pub type_name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

impl SetVarTypeArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum StringsCommands {
    /// List strings already defined in the program
    #[command(
        alias = "ls",
        after_help = "Example:\n  ghidra strings list --filter 'value~error' --fields address,value"
    )]
    List(QueryOptions),
    /// Get references to a string
    #[command(alias = "references", alias = "xrefs")]
    Refs(StringRefsArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct StringRefsArgs {
    pub string: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum SymbolCommands {
    /// List symbols with optional filters and field selection
    #[command(
        alias = "ls",
        after_help = "Example:\n  ghidra symbol list --filter 'name^init' --fields address,name"
    )]
    List(QueryOptions),
    /// Get symbol details
    Get(SymbolGetArgs),
    /// Create symbol
    Create(CreateSymbolArgs),
    /// Delete symbol
    Delete(SymbolGetArgs),
    /// Rename symbol
    Rename(RenameArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SymbolGetArgs {
    pub name: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct CreateSymbolArgs {
    pub address: String,
    pub name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum MemoryCommands {
    /// Show memory map
    Map(QueryOptions),
    /// Read memory
    Read(MemReadArgs),
    /// Write memory
    Write(MemWriteArgs),
    /// Search memory for a hex byte pattern
    Search(MemSearchArgs),
}

#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct MemReadArgs {
    pub address: String,
    pub size: usize,
    pub options: QueryOptions,
}

// Both CLI forms map to the existing serialized `size` field.
#[derive(Args)]
#[command(group(clap::ArgGroup::new("byte_count").required(true).args(["size", "length"])))]
struct MemReadCliArgs {
    address: String,
    /// Number of bytes to read, in decimal or hexadecimal
    #[arg(value_name = "BYTES", value_parser = parse_memory_read_size)]
    size: Option<usize>,
    /// Alternate form for the number of bytes to read
    #[arg(long, value_name = "BYTES", value_parser = parse_memory_read_size)]
    length: Option<usize>,
    #[command(flatten)]
    options: QueryOptions,
}

impl Args for MemReadArgs {
    fn augment_args(cmd: clap::Command) -> clap::Command {
        MemReadCliArgs::augment_args(cmd)
    }

    fn augment_args_for_update(cmd: clap::Command) -> clap::Command {
        MemReadCliArgs::augment_args_for_update(cmd)
            .mut_group("byte_count", |group| group.required(false))
    }
}

impl clap::FromArgMatches for MemReadArgs {
    fn from_arg_matches(matches: &clap::ArgMatches) -> Result<Self, clap::Error> {
        Self::from_arg_matches_mut(&mut matches.clone())
    }

    fn from_arg_matches_mut(matches: &mut clap::ArgMatches) -> Result<Self, clap::Error> {
        let args = <MemReadCliArgs as clap::FromArgMatches>::from_arg_matches_mut(matches)?;
        Ok(Self {
            address: args.address,
            size: args
                .size
                .or(args.length)
                .expect("clap requires a byte count"),
            options: args.options,
        })
    }

    fn update_from_arg_matches(&mut self, matches: &clap::ArgMatches) -> Result<(), clap::Error> {
        self.update_from_arg_matches_mut(&mut matches.clone())
    }

    fn update_from_arg_matches_mut(
        &mut self,
        matches: &mut clap::ArgMatches,
    ) -> Result<(), clap::Error> {
        if let Some(address) = matches.remove_one("address") {
            self.address = address;
        }
        if let Some(size) = matches
            .remove_one("size")
            .or_else(|| matches.remove_one("length"))
        {
            self.size = size;
        }
        clap::FromArgMatches::update_from_arg_matches_mut(&mut self.options, matches)
    }
}

fn parse_memory_read_size(value: &str) -> Result<usize, String> {
    let digits = value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"));
    let size = match digits {
        Some(digits) if !digits.starts_with('+') => usize::from_str_radix(digits, 16).ok(),
        Some(_) => None,
        None => value.parse::<usize>().ok(),
    };
    // The bridge reads the count as a Java int.
    size.filter(|&size| size <= i32::MAX as usize)
        .ok_or_else(|| {
            format!(
                "Use a decimal or hexadecimal byte count from 0 to {}",
                i32::MAX
            )
        })
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct MemWriteArgs {
    pub address: String,
    pub bytes: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct MemSearchArgs {
    /// Hex bytes to search for (e.g. `deadbeef` or `de ad be ef`)
    pub pattern: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum XRefCommands {
    /// Get cross-references to address
    To(XRefArgs),
    /// Get cross-references from address
    From(XRefArgs),
    /// List all cross-references
    List(XRefArgs),
    /// Inspect every function with a direct reference to an address
    #[command(alias = "trace")]
    TraceTo(XRefTraceArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct XRefArgs {
    /// XRef target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// XRef target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl XRefArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct XRefTraceArgs {
    /// Referenced address or symbol
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Include callers for each referencing function
    #[arg(long)]
    pub callers: bool,
    /// Include callees for each referencing function
    #[arg(long)]
    pub callees: bool,
    /// Include function-entry xrefs for each referencing function
    #[arg(long)]
    pub xrefs: bool,
    /// Number of instructions to disassemble for each referencing function
    #[arg(long)]
    pub disasm: Option<usize>,
    /// Refuse larger source-function sets unless the analyst explicitly raises the bound
    #[arg(long, default_value_t = 20)]
    pub max_functions: usize,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl XRefTraceArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum TypeCommands {
    /// List data types
    #[command(alias = "ls")]
    List(QueryOptions),
    /// Get type definition
    Get(TypeGetArgs),
    /// Create type
    Create(CreateTypeArgs),
    /// Apply type to address
    Apply(ApplyTypeArgs),
    /// Delete a data type
    #[command(alias = "rm")]
    Delete(TypeDeleteArgs),
    /// Rename a data type
    #[command(alias = "mv")]
    Rename(TypeRenameArgs),
    /// Create an enum type
    CreateEnum(CreateEnumArgs),
    /// Create a typedef (type alias)
    Typedef(TypedefArgs),
    /// Add a field to a struct type
    AddField(TypeAddFieldArgs),
    /// Remove a field from a struct type
    DelField(TypeDelFieldArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct TypeGetArgs {
    pub name: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct CreateTypeArgs {
    pub definition: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ApplyTypeArgs {
    pub address: String,
    pub type_name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct TypeDeleteArgs {
    /// Name or path of the type to delete
    pub name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct TypeRenameArgs {
    /// Current name of the type
    pub old_name: String,
    /// New name for the type
    pub new_name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct CreateEnumArgs {
    /// Enum type name
    pub name: String,
    /// Comma-separated KEY=VALUE pairs, e.g. "RED=0,GREEN=1,BLUE=2"
    #[arg(long)]
    pub values: String,
    /// Size in bytes (1, 2, 4, or 8)
    #[arg(long, default_value = "4")]
    pub size: i32,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct TypedefArgs {
    /// Name for the new typedef
    pub name: String,
    /// Base type to alias (e.g., "int", "dword", "MyStruct")
    pub base_type: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct TypeAddFieldArgs {
    /// Name of the struct type to modify
    pub type_name: String,
    /// Field name
    #[arg(long)]
    pub name: String,
    /// Field type (e.g., "int", "byte", "pointer", a custom struct name)
    #[arg(long = "type")]
    pub field_type: String,
    /// Offset within the struct (if omitted, appends at end)
    #[arg(long)]
    pub offset: Option<i32>,
    /// Field size override
    #[arg(long)]
    pub size: Option<i32>,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct TypeDelFieldArgs {
    /// Name of the struct type to modify
    pub type_name: String,
    /// Field name to remove
    #[arg(long)]
    pub name: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum CommentCommands {
    /// List all comments
    #[command(alias = "ls")]
    List(QueryOptions),
    /// Get comment at address
    Get(CommentGetArgs),
    /// Set comment
    Set(CommentSetArgs),
    /// Delete comment
    Delete(CommentGetArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct CommentGetArgs {
    pub address: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct CommentSetArgs {
    pub address: String,
    pub text: String,
    #[arg(long)]
    pub comment_type: Option<String>,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum FindCommands {
    /// Find strings
    #[command(alias = "str", alias = "strings")]
    String(FindStringArgs),
    /// Find byte patterns
    Bytes(FindBytesArgs),
    /// Find functions
    #[command(alias = "func", alias = "fn", alias = "functions")]
    Function(FindFunctionArgs),
    /// Find calls to function
    Calls(FindCallsArgs),
    /// Find crypto constants
    #[command(alias = "encryption")]
    Crypto(QueryOptions),
    /// Find interesting functions
    #[command(alias = "suspicious", alias = "notable")]
    Interesting(QueryOptions),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct FindStringArgs {
    pub pattern: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct FindBytesArgs {
    pub hex: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct FindFunctionArgs {
    pub pattern: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct FindCallsArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl FindCallsArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum GraphCommands {
    /// Call graph
    Calls(QueryOptions),
    /// Get callers of function
    #[command(alias = "called-by", alias = "incoming")]
    Callers(GraphFunctionArgs),
    /// Get callees of function
    #[command(alias = "calls-to", alias = "outgoing")]
    Callees(GraphFunctionArgs),
    /// Export graph
    Export(GraphExportArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct GraphFunctionArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    #[arg(long)]
    pub depth: Option<usize>,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl GraphFunctionArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct GraphExportArgs {
    /// Export format (e.g., dot, json)
    #[arg(id = "export_format")]
    pub format: String,
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct DecompileArgs {
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Function target (name | 0xaddr | FUN_<hex>)
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Include local variable details (name, type, storage)
    #[arg(long)]
    pub with_vars: bool,
    /// Include parameter details (name, type, storage)
    #[arg(long)]
    pub with_params: bool,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl DecompileArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct DisasmArgs {
    /// Start address or symbol (for example, 0x401000, main, or FUN_00401000)
    #[arg(value_name = "TARGET", required_unless_present = "target")]
    pub positional_target: Option<String>,
    /// Alternate form for the start address or symbol
    #[arg(long = "target", value_name = "TARGET")]
    pub target: Option<String>,
    /// Maximum instructions to read (default: 10)
    #[arg(long = "instructions", short = 'n', value_name = "N")]
    pub num_instructions: Option<usize>,
    #[command(flatten)]
    pub options: QueryOptions,
}

impl DisasmArgs {
    pub fn resolved_target(&self) -> &str {
        self.target
            .as_deref()
            .or(self.positional_target.as_deref())
            .expect("clap should ensure target is provided")
    }
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum DiffCommands {
    /// Compare two programs
    Programs(DiffProgramsArgs),
    /// Compare functions
    Functions(DiffFunctionsArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct DiffProgramsArgs {
    pub program1: String,
    pub program2: String,
    #[arg(long)]
    pub format: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct DiffFunctionsArgs {
    /// First function (name or address)
    pub func1: String,
    /// Second function (name or address)
    pub func2: String,
    #[arg(long)]
    pub format: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum DumpCommands {
    /// Dump imports
    Imports(QueryOptions),
    /// Dump exports
    Exports(QueryOptions),
    /// Dump functions
    Functions(QueryOptions),
    /// Dump strings
    Strings(QueryOptions),
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum PatchCommands {
    /// Patch bytes
    Bytes(PatchBytesArgs),
    /// NOP instructions
    Nop(PatchNopArgs),
    /// Export patched binary
    Export(PatchExportArgs),
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct PatchBytesArgs {
    pub address: String,
    pub hex: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct PatchNopArgs {
    pub address: String,
    #[arg(long)]
    pub count: Option<usize>,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct PatchExportArgs {
    #[arg(short, long)]
    pub output: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum ScriptCommands {
    /// Run a script file
    Run(ScriptRunArgs),
    /// Compile a Java script without executing it (checks for errors)
    Check(ScriptCheckArgs),
    /// Execute inline Python code
    Python(ScriptInlineArgs),
    /// Execute inline Java code
    Java(ScriptInlineArgs),
    /// List available scripts
    List,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ScriptRunArgs {
    pub script_path: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
    /// Expected output artifact: PATH or PATH:MIN_ROWS (repeatable). The job
    /// fails if the artifact is missing, empty, or below MIN_ROWS.
    #[arg(long = "expect", value_name = "PATH[:MIN_ROWS]")]
    pub expect: Vec<String>,
    /// Allow an expected artifact to exist but be empty.
    #[arg(long)]
    pub allow_empty: bool,
    /// Persist successful script changes by clean bridge teardown (stops the bridge).
    #[arg(long)]
    pub save: bool,
    /// Script arguments (after --)
    #[arg(last = true)]
    pub args: Vec<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ScriptCheckArgs {
    /// Script file to compile (without executing)
    pub script_path: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ScriptInlineArgs {
    pub code: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct BatchArgs {
    /// Batch file, or '-' to read commands from stdin
    pub script_file: String,

    #[arg(long)]
    pub project: Option<String>,

    #[arg(long)]
    pub program: Option<String>,

    /// Continue running remaining commands after a failure instead of
    /// stopping at the first error. By default the batch stops on the
    /// first error and exits non-zero.
    #[arg(long)]
    pub continue_on_error: bool,

    /// Reject every command unless the whole batch is provably read-only
    #[arg(long)]
    pub read_only: bool,

    /// Refuse larger batches unless the analyst explicitly raises the bound
    #[arg(long, default_value_t = 100)]
    pub max_commands: usize,
}

#[derive(Subcommand, Clone, Serialize, Deserialize, Debug)]
pub enum ConfigCommands {
    /// List all configuration
    List,
    /// Get configuration value
    Get { key: String },
    /// Set configuration value
    Set { key: String, value: String },
    /// Reset configuration
    Reset,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SetDefaultArgs {
    pub kind: String,
    pub value: String,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SummaryArgs {
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct StatsArgs {
    #[command(flatten)]
    pub options: QueryOptions,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct ImportArgs {
    pub binary: String,
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
    /// Import only — skip auto-analysis (the program is still persisted)
    #[arg(long, default_value = "false")]
    pub no_analyze: bool,
    /// Return immediately, let bridge continue import in background
    #[arg(long, default_value = "false")]
    pub detach: bool,
}

#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct AnalyzeArgs {
    #[arg(long)]
    pub program: Option<String>,
    #[arg(long)]
    pub project: Option<String>,
    /// Return immediately, let bridge continue analysis in background
    #[arg(long, default_value = "false")]
    pub detach: bool,
}

/// Common query options used across commands
#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct QueryOptions {
    /// Program within the selected project
    #[arg(long)]
    pub program: Option<String>,

    /// Project name or path
    #[arg(long)]
    pub project: Option<String>,

    /// Filter expression: <field><op><value>, e.g. 'name~PK' (contains),
    /// 'name=~"^PK_"' (regex), 'size>100'. Ops: = != > >= < <= ~ ^ $ =~.
    /// Combine with AND/OR/NOT. Bare words are rejected.
    #[arg(short, long)]
    pub filter: Option<String>,

    /// Select comma-separated fields (use --fields=-FIELD to exclude)
    #[arg(long, long_help = FIELDS_LONG_HELP)]
    pub fields: Option<String>,

    /// Output format, e.g. compact, json, ndjson, csv, tsv, or table
    #[arg(long, short = 'o', long_help = FORMAT_LONG_HELP)]
    pub format: Option<String>,

    /// Maximum number of results (0 = unlimited; default 50)
    #[arg(long)]
    pub limit: Option<usize>,

    /// Skip the first N matching results
    #[arg(long)]
    pub offset: Option<usize>,

    /// Sort by comma-separated fields; prefix with '-' for descending (e.g. --sort=-size)
    #[arg(long, allow_hyphen_values = true)]
    pub sort: Option<String>,

    /// Print only the count, with any explicit --limit and --offset
    #[arg(long)]
    pub count: bool,

    /// Print compact JSON (use --pretty for indented JSON)
    #[arg(long)]
    pub json: bool,
}

/// Arguments for the setup command
#[derive(Args, Clone, Serialize, Deserialize, Debug)]
pub struct SetupArgs {
    /// Specific Ghidra version to install (e.g., "11.0"). Defaults to latest.
    #[arg(long)]
    pub version: Option<String>,

    /// Installation directory. Defaults to standard data directory.
    #[arg(long, short = 'd')]
    pub dir: Option<String>,

    /// Skip Java check
    #[arg(long)]
    pub force: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_decompile_target_flag() {
        let cli = Cli::try_parse_from(["ghidra", "decompile", "--target", "FUN_00401000"])
            .expect("decompile --target should parse");
        match cli.command {
            Commands::Decompile(args) => assert_eq!(args.resolved_target(), "FUN_00401000"),
            _ => panic!("expected decompile command"),
        }
    }

    #[test]
    fn parses_function_get_positional_target() {
        let cli = Cli::try_parse_from(["ghidra", "function", "get", "main"])
            .expect("function get positional target should parse");
        match cli.command {
            Commands::Function(FunctionCommands::Get(args)) => {
                assert_eq!(args.resolved_target(), "main");
            }
            _ => panic!("expected function get command"),
        }
    }

    #[test]
    fn inspect_preserves_single_target_flag() {
        let cli = Cli::try_parse_from(["ghidra", "inspect", "--target", "FUN_00401000"])
            .expect("single inspect --target should parse");
        match cli.command {
            Commands::Inspect(args) => {
                assert_eq!(args.resolved_targets(), vec!["FUN_00401000"]);
                assert_eq!(args.max_targets, 20);
            }
            _ => panic!("expected inspect command"),
        }
    }

    #[test]
    fn inspect_accepts_multiple_positional_targets() {
        let cli = Cli::try_parse_from([
            "ghidra",
            "inspect",
            "0x100",
            "FUN_00000200",
            "main",
            "--decompile",
            "--max-targets",
            "3",
        ])
        .expect("multi-target inspect should parse");
        match cli.command {
            Commands::Inspect(args) => {
                assert_eq!(
                    args.resolved_targets(),
                    vec!["0x100", "FUN_00000200", "main"]
                );
                assert!(args.decompile);
                assert_eq!(args.max_targets, 3);
            }
            _ => panic!("expected inspect command"),
        }
    }

    #[test]
    fn inspect_rejects_mixed_target_forms() {
        assert!(Cli::try_parse_from(["ghidra", "inspect", "0x100", "--target", "0x200"]).is_err());
    }

    #[test]
    fn parses_xref_trace_to_with_explicit_bound() {
        let cli = Cli::try_parse_from([
            "ghidra",
            "xref",
            "trace-to",
            "0xfebe0000",
            "--disasm",
            "20",
            "--max-functions",
            "7",
        ])
        .expect("xref trace-to should parse");
        match cli.command {
            Commands::XRef(XRefCommands::TraceTo(args)) => {
                assert_eq!(args.resolved_target(), "0xfebe0000");
                assert_eq!(args.disasm, Some(20));
                assert_eq!(args.max_functions, 7);
            }
            _ => panic!("expected xref trace-to command"),
        }
    }

    #[test]
    fn parses_bounded_read_only_stdin_batch() {
        let cli = Cli::try_parse_from([
            "ghidra",
            "batch",
            "--read-only",
            "--max-commands",
            "12",
            "-",
        ])
        .expect("stdin batch should parse");
        match cli.command {
            Commands::Batch(args) => {
                assert_eq!(args.script_file, "-");
                assert!(args.read_only);
                assert_eq!(args.max_commands, 12);
            }
            _ => panic!("expected batch command"),
        }
    }
}
