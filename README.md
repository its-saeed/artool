# Artool
This tool is proposed by Artem and supposed to help him. That's why it's called Artool :D

# How to add new log type
Logs is expected to be like this:
```log
[7f3606ffd6c0][21-03-22T10:18:49.218][EvmClient.cpp:185   ][CallRunner          ] ARTEM_SAEED DUMMY_LOG this is a dummy log 34.21.222.37 just for testing
```

* We have `ARTEM_SAEED` as the magic phrase.
* Then `log_type` should be present. `log_type` is supposed to have only UPPERCASE letters and `_` . Technically speaking, it should be in `[A-Z_]+` format. For example here `DUMMY_LOG` is the log type.

If your new proposed log have above conditions, do the following steps to support it:

1. Define your log type like what we did already:
```python
LOG_TYPE_INTRO = "INTRO"
LOG_TYPE_DNS_TEST = "DNS_TEST"      # For testing this script
LOG_TYPE_DUMMY = "DUMMY"      # For testing this script
```
2. let's supposed you want to add `foo_log`. You need to define a function named `process_foo_log`. Do whatever you want to do with these class of logs in the function.
3. Don't forget to add this function and it's `elif` entry in `process_line` function.