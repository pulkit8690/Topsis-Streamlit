
# Topsis Library and Web App

Web app Link [topsis web app](https://pulkit-topsis-web-app.streamlit.app/)

Package link [topsis package](https://pypi.org/project/topsis-pulkit-102103267/)

TOPSIS( Technique for order for preference by similarity to Ideal solution ) for MCDM (Multiple criteria decision making) in Python compiled by Pulkit Arora, 102103267, TIET, Patiala. 


## Installation
Use the package manager pip to install.
```
pip install topsis_pulkit_102103267
```
## Usage
Enter csv filename followed by .csv extentsion, then enter the weights vector with vector values separated by commas, followed by the impacts vector with comma separated signs (+,-) and enter the output file name followed by .csv extension.

```topsis_pulkit_102103267 [InputDataFile as .csv] [Weights as a string] [Impacts as a string] [ResultFileName as .csv]```

### Example
```topsis_pulkit_102103267 sample.csv "1,1,1,1" "-,+,+,+" output.csv```

### Sample Input
| Fund  | P1    | P2	| P3	| P4	| P5	|
| :---: | :---: | :---: | :---: | :---: | :---: |
| M1	| 0.72	| 0.52	| 7	    | 56	| 16.06 |
| M2	| 0.83	| 0.69	| 3.7	| 37	| 10.56 |
| M3	| 0.81	| 0.66	| 4	    | 30.4	| 8.97  | 
| M4	| 0.77	| 0.59	| 3.6	| 44.1	| 12.27 |
| M5	| 0.82	| 0.67	| 7	    | 34.6	| 10.77 |
| M6	| 0.72	| 0.52	| 3	    | 58.5	| 15.69 |
| M7	| 0.85	| 0.72	| 4.2	| 50.5	| 14.07 |
| M8	| 0.64	| 0.41	| 3	    | 38.5	| 10.64 |

### Sample Output
| Fund  | P1    | P2	| P3	| P4	| P5	|     TOPSIS Score   | Rank  |
| :---: | :---: | :---: | :---: | :---: | :---: |        :---:       | :---: |
| M1	| 0.72	| 0.52	| 7	    | 56	| 16.06 | 0.6339125495800909 |   1   |
| M2	| 0.83	| 0.69	| 3.7	| 37	| 10.56 | 0.3751667010618832 |   6   |
| M3	| 0.81	| 0.66	| 4	    | 30.4	| 8.97  | 0.4268895365063883 |   3   |
| M4	| 0.77	| 0.59	| 3.6	| 44.1	| 12.27 | 0.3631574031053784 |   8   |
| M5	| 0.82	| 0.67	| 7	    | 34.6	| 10.77 | 0.6320591213396627 |   2   |
| M6	| 0.72	| 0.52	| 3	    | 58.5	| 15.69 | 0.3687064767204701 |	 7   |
| M7	| 0.85	| 0.72	| 4.2	| 50.5	| 14.07 | 0.3862956874804864 |	 5   |
| M8	| 0.64	| 0.41	| 3	    | 38.5	| 10.64 | 0.4069761888395339 |   4   |



## Note
- The first column and first row are removed by the library before processing, in attempt to remove indices and headers. So the csv MUST follow the format as shown in sample.csv shown in the Example section.
- The input data file MUST contain three or more columns.
- The second to last columns of the data file MUST contain NUMERIC values.
- The number of weights, impacts and columns (second to last) MUST be SAME.
- Impacts MUST either be '+' or '-'.
- Impacts and Weights MUST be separated by , (comma).
## License

© 2024 Pulkit Arora

This repository is licensed under MIT License. See LICENSE for details.
## Web App Screenshots

![Image Alt Text](![image](https://github.com/pulkit8690/Topsis-Streamlit/assets/103959073/5e4e7ac0-ee39-4e6d-a86c-d5a5e8f52471)
)
