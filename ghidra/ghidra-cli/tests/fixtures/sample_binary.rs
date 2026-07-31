//! Sample binary for E2E testing of ghidra-cli.
//! 
//! This binary contains various functions and data structures
//! that can be analyzed by Ghidra to test the CLI functionality.

use std::collections::HashMap;

/// A simple structure for testing
#[repr(C)]
struct TestStruct {
    value: i32,
    name: [u8; 32],
}

/// Global constant string for testing string detection
static HELLO_WORLD: &str = "Hello, Ghidra CLI!";
static VERSION_STRING: &str = "test_binary v1.0.0";
static SECRET_KEY: &str = "super_secret_key_12345";

/// Simple arithmetic function
#[no_mangle]
pub extern "C" fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}

/// Multiply function
#[no_mangle]
pub extern "C" fn multiply(x: i32, y: i32) -> i32 {
    x * y
}

/// Calculate factorial (recursive)
#[no_mangle]
pub extern "C" fn factorial(n: u64) -> u64 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

/// Fibonacci (iterative)
#[no_mangle]
pub extern "C" fn fibonacci(n: u32) -> u64 {
    if n == 0 {
        return 0;
    }
    if n == 1 {
        return 1;
    }
    
    let mut a = 0u64;
    let mut b = 1u64;
    
    for _ in 2..=n {
        let temp = a + b;
        a = b;
        b = temp;
    }
    
    b
}

/// String processing function
#[no_mangle]
pub extern "C" fn process_string(input: *const u8, len: usize) -> i32 {
    if input.is_null() || len == 0 {
        return -1;
    }
    
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    let mut sum: i32 = 0;
    
    for &byte in slice {
        sum += byte as i32;
    }
    
    sum
}

/// XOR encryption (simple cipher for testing)
#[no_mangle]
pub extern "C" fn xor_encrypt(data: *mut u8, len: usize, key: u8) {
    if data.is_null() || len == 0 {
        return;
    }
    
    let slice = unsafe { std::slice::from_raw_parts_mut(data, len) };
    
    for byte in slice.iter_mut() {
        *byte ^= key;
    }
}

/// Hash function (simple for testing)
#[no_mangle]
pub extern "C" fn simple_hash(data: *const u8, len: usize) -> u32 {
    if data.is_null() || len == 0 {
        return 0;
    }
    
    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    let mut hash: u32 = 5381;
    
    for &byte in slice {
        hash = hash.wrapping_mul(33).wrapping_add(byte as u32);
    }
    
    hash
}

/// Initialize a TestStruct
#[no_mangle]
pub extern "C" fn init_struct(ts: *mut TestStruct, value: i32) {
    if ts.is_null() {
        return;
    }
    
    unsafe {
        (*ts).value = value;
        (*ts).name = [0; 32];
    }
}

/// Internal helper (not exported)
fn internal_helper(x: i32) -> i32 {
    x * 2 + 1
}

/// Main function that uses the other functions
fn main() {
    println!("{}", HELLO_WORLD);
    println!("{}", VERSION_STRING);
    
    let sum = add_numbers(10, 20);
    println!("10 + 20 = {}", sum);
    
    let product = multiply(5, 6);
    println!("5 * 6 = {}", product);
    
    let fact = factorial(10);
    println!("10! = {}", fact);
    
    let fib = fibonacci(20);
    println!("fib(20) = {}", fib);
    
    let hash = simple_hash(SECRET_KEY.as_ptr(), SECRET_KEY.len());
    println!("hash = {:x}", hash);
    
    let helper_result = internal_helper(42);
    println!("internal: {}", helper_result);
    
    // Create a simple lookup table
    let mut lookup: HashMap<&str, i32> = HashMap::new();
    lookup.insert("one", 1);
    lookup.insert("two", 2);
    lookup.insert("three", 3);
    
    for (key, value) in &lookup {
        println!("{} = {}", key, value);
    }
}
