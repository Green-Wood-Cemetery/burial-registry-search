# Shell Scripts

The shell scripts are just a convenient way to make easier to execute the steps. The python scripts are used by them, so the efect is the same as execute the python scripts directly.

We have 2 types of shell scripts: the single and the full execution scripts.


## Single Execution Scripts

Single execution scripts will be used when you need to process a new volume or reprocess (fix data) an existing volume. When you need to run then, the correct order is:
1) single_convert.sh
2) single_load.sh
3) single_validate_import.sh

See in the next sections more details about each script.


### single_convert.sh

Convert one excel file into json file. It uses only one positional parameter that is the number of the volume.

```
$ ./single_convert.sh <volume number>
```

> Example:
>
> $ ./single_convert.sh 10
>
> This will convert the Excel file for volume 10 into a json.


This script generates a log of the execution, that can be found at:


```
folder: data/logs
file name: excel-to-es-volume-<volume number>-<timestamp>.csv
```


### single_load.sh

Import the json file, cleaning the index before loading. It uses two positional parameters: the number of the volume and the index name.

```
$ ./single_load.sh <volume number> <index name>
```

> Example:
>
> $ ./single_load.sh 40 test-index
>
> This will load all the volume 40 json data into index called test-index


This script generates a log of the execution, that can be found at:


```
folder: data/logs
file name: import-data-<index name>-<volume number>-<timestamp>.csv
```

You can also check for file called `import_errors.json` to see the records that were not imported. This file is not cleaned up at every execution, so do it manually.


### single_validate_import.sh

Validate if the json file and the content imported on the index really match. It uses two positional parameters: the number of the volume and the index name.

```
$ ./single_validate_import.sh <volume number> <index name>
```

> Example:
>
> $ ./single_validate_import.sh 40 test-index
>
> This will compare the volume 40 json data with the content inside the index called test-index for the volume 40


This script generates a log of the execution, that can be found at:


```
folder: data/logs
file name: compare-index-<index name>-<timestamp>.csv
```

Besides the log file of the execution on the logs folder, it also generates two other files: 
- `validate_size.csv`that contains the record count comparison between index and file, and 
- `validate_values.csv`, that contains field by field the differences between index and file.
  

## Full Execution Scripts

Full execution scripts will be used when you need to process all the volumes. When you need to run then, the correct order is:
1) full_convert.sh
2) full_load.sh
3) full_validate_import.sh

See in the next sections more details about each script.

> All the full scripts contain a for loop that executes from 1 to 60. If more volumes are added to this data, the for loops need to be changed.


### full_convert.sh

Convert all excel files into json files. It uses no positional parameter.

```
$ ./full_convert.sh
```

> Example:
>
> $ ./full_convert.sh


This script generates a log of the execution for each volume processed, that can be found at:


```
folder: data/logs
file name: excel-to-es-volume-<volume number>-<timestamp>.csv
```


### full_load.sh

Import the json file, cleaning the index before loading. It uses one positional parameter: the index name.

```
$ ./full_load.sh <index name>
```

> Example:
>
> $ ./full_load.sh test-index
>
> This will load all the volumes json data into index called test-index


This script generates a log of the execution for each volume processed, that can be found at:


```
folder: data/logs
file name: import-data-<index name>-<volume number>-<timestamp>.csv
```

You can also check for file called `import_errors.json` to see the records that were not imported. This file is not cleaned up at every execution, so do it manually.


### full_validate_import.sh

Validate if the json file and the content imported on the index really match. It uses one positional parameter: the index name.

```
$ ./full_validate_import.sh <index name>
```

> Example:
>
> $ ./full_validate_import.sh test-index
>
> This will compare all the volumes json data with the content inside the index called test-index


This script generates a log of the execution that can be found at:


```
folder: data/logs
file name: compare-index-<index name>-<timestamp>.csv
```

Besides the log file of the execution on the logs folder, it also generates two other files: 
- `validate_size.csv`that contains the record count comparison between index and file, and 
- `validate_values.csv`, that contains field by field the differences between index and file.
  

