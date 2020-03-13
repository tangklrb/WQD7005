import numpy as np
import pandas as pd

exam_data = {
    'name': ['Ali', 'Abu', 'Katherine', 'Site', 'Emily', 'Michael', 'Matthew', 'Laura', 'Kevin', 'James'],
    'score': [12.5, 9, 16.5, np.nan, 9, 20, 14.5, np.nan, 8, 19],
    'attempts': [1, 3, 2, 3, 2, 3, 1, 1, 2, 1],
    'qualify': ['yes', 'no', 'yes', 'no', 'no', 'yes', 'yes', 'no', 'no', 'yes']
}

exam_df = pd.DataFrame.from_dict(exam_data)
print(
    'Dataset\n',
    exam_df
)

# Question 1
print(
    '\nQuestion 1\n',
    exam_df[['name', 'score']].sort_values(by='score', ascending=False)
)

# Question 2
print(
    '\nQuestion 2\n',
    exam_df.loc[[1, 3, 5, 6], ['name', 'attempts', 'score']]
)

# Question 3

print(
    '\nQuestion 3\n',
    exam_df[exam_df['attempts'] > 2]
)

# Question 4
print(
    '\nQuestion 4',
    '\nrow_count:', exam_df.shape[0],
    '\ncolumn_count:', exam_df.shape[1],
    '\n'
)

# Question 5
print(
    'Question 5\n',
    exam_df[exam_df['score'].isnull()]
)

# Question 6
print(
    '\nQuestion 6\n',
    exam_df[(exam_df['score'] >= 12) & (exam_df['score'] <= 20)]
)

# Question 7
print(
    '\nQuestion 7\n',
    exam_df[(exam_df['score'] > 10) & (exam_df['attempts'] < 2)]
)

# Question 8
exam_df.at[3, 'score'] = 11.5
print(
    '\nQuestion 8\n',
    exam_df
)

# Question 9
print(
    '\nQuestion 9\n',
    'Sum of Student attempts:', exam_df['attempts'].sum()
)

# Question 10
print(
    '\nQuestion 1',
    '\nMean Score =', exam_df['score'].mean(),
    '\n', exam_df[exam_df['score'] >= exam_df['score'].mean()][['name', 'score']].sort_values(by='score', ascending=False)
)

'''
Output:
Dataset
         name  score  attempts qualify
0        Ali   12.5         1     yes
1        Abu    9.0         3      no
2  Katherine   16.5         2     yes
3       Site    NaN         3      no
4      Emily    9.0         2      no
5    Michael   20.0         3     yes
6    Matthew   14.5         1     yes
7      Laura    NaN         1      no
8      Kevin    8.0         2      no
9      James   19.0         1     yes

Question 1
         name  score
5    Michael   20.0
9      James   19.0
2  Katherine   16.5
6    Matthew   14.5
0        Ali   12.5
1        Abu    9.0
4      Emily    9.0
8      Kevin    8.0
3       Site    NaN
7      Laura    NaN

Question 2
       name  attempts  score
1      Abu         3    9.0
3     Site         3    NaN
5  Michael         3   20.0
6  Matthew         1   14.5

Question 3
       name  score  attempts qualify
1      Abu    9.0         3      no
3     Site    NaN         3      no
5  Michael   20.0         3     yes

Question 4 
row_count: 10 
column_count: 4 

Question 5
     name  score  attempts qualify
3   Site    NaN         3      no
7  Laura    NaN         1      no

Question 6
         name  score  attempts qualify
0        Ali   12.5         1     yes
2  Katherine   16.5         2     yes
5    Michael   20.0         3     yes
6    Matthew   14.5         1     yes
9      James   19.0         1     yes

Question 7
       name  score  attempts qualify
0      Ali   12.5         1     yes
6  Matthew   14.5         1     yes
9    James   19.0         1     yes

Question 8
         name  score  attempts qualify
0        Ali   12.5         1     yes
1        Abu    9.0         3      no
2  Katherine   16.5         2     yes
3       Site   11.5         3      no
4      Emily    9.0         2      no
5    Michael   20.0         3     yes
6    Matthew   14.5         1     yes
7      Laura    NaN         1      no
8      Kevin    8.0         2      no
9      James   19.0         1     yes

Question 9
 Sum of Student attempts: 19

Question 1 
Mean Score = 13.333333333333334 
         name  score
5    Michael   20.0
9      James   19.0
2  Katherine   16.5
6    Matthew   14.5

Process finished with exit code 0

'''