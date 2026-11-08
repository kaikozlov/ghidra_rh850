# Follow-ups

- Review the integration import deadlines under concurrent analysis load.
  `tests/project_tests.rs::test_import_binary` and the shared-project setup in
  `tests/common/mod.rs` allow 300 seconds for `import`, which includes analysis;
  the separate setup `analyze` step allows 600 seconds.
