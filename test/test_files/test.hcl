file_type = "hcl"
test_string = "testing"
test_bool_true = true
test_bool_false = false
test_int = 123
test_float = 123.123
test_dict = {
  "hcl_dict_key" = "hcl_dict_value"
}
test_list = [
  "test1",
  "test2",
  "test3"
]

test_hcl "test_hcl_name" {
    test_hcl_key = "test_hcl_value"
}
