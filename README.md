# Fortilog picker

Output only specified fields from Fortigate CSV logfile (format: "field1=value","field2=value",...).

## Usage

```bash
# input from stdin, output to stdout ("-f" or "--field" option is required):
$ fortilog-pick.py -f sample_field.txt < sample_log.csv

# input from file, output to stdout:
$ fortilog-pick.py -f sample_field.txt sample_log.csv

# Support for gzip compressed file
$ fortilog-pick.py -f sample_field.txt sample_log.csv.gz

# You can use wildcards for file name:
$ fortilog-pick.py -f sample_field.txt *.csv *.csv.gz

# By "-o" or "--csv" option, output to csv file (output filename: "logname-yyyymmdd-hhmmss.csv"):
$ fortilog-pick.py -f sample_field.txt -o sample_log.csv

# If the "--field" option is not specified, fields are selected by the GUI.
$ fortilog-pick.py sample_log.csv
```

## Input and Output CSV File Format

- Input File (ex: "sample_log.csv"):

```csv
field1=1,field2=2,field3=3,field4=4
field1=a,field2=b,field3=c,field4=d
field1=A,field2=B,field4=D
```

- field file (ex: "sample_field.txt"):

```text
field4
field3
field1
field5
```

- Output File (ex: "sample_log.csv-yyyymmdd-hhmmss.csv"):

```csv
field4,field3,field1,field5
4,3,1,
d,c,a,
D,,A,
```
