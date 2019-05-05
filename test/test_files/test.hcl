file_type = "hcl"
test_string = "testing"
test_bool_true = true
test_bool_false = false
test_int = 123.0
test_float = 123.123
test_list = [
  "test1",
  "test2",
  "test3"
]

test_hcl "test_hcl_name" {
    test_hcl_key = "the AMI test_hcl_value use"
}
