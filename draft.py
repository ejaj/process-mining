# import pandas as pd
#
# # Your existing dataframe
# data = {
#     "STUDIENR": ["STNR000001", "STNR000001", "STNR000001", "STNR000001", "STNR000001", "STNR000002"],
#     "KURSKODE": [2402, 28213, 41632, 41656, 41661, 28213],
#     "KURSTXT": [
#         "2402 Introduktion til statistik",
#         "28213 Polymerteknologi",
#         "41632 Robust design af produkter og mekanismer",
#         "41656 Materialer i avancerede anvendelser og p...",
#         "41661 Metallære",
#         "2402 Introduktion til statistik",
#     ],
#     "BEDOMMELSE": [4.0, 7.0, 7.0, 10.0, 10.0, 9.0],
#     "ECTS": [5.0, 5.0, 5.0, 10.0, 5.0, 5.0],
#     "BEDOMMELSESDATO": [
#         "2018-12-19",
#         "2019-12-30",
#         "2019-06-07",
#         "2020-05-27",
#         "2018-12-18",
#         "2018-12-19",
#     ],
# }
#
# df = pd.DataFrame(data)
#
# # Prerequisite courses dictionary
# prerequisite_courses = {
#     "2402": ["28213", "41656"],
#     "41656": ["41661"]
# }
#
# # Add a new column "total_pr" to the dataframe
# df["total_pr"] = 0
# df["total_pr_BEDOMMELSE"] = 0
#
# # Iterate through unique "STUDIENR" values
# for studienr in df["STUDIENR"].unique():
#     # Create a mask for the current "STUDIENR"
#     mask = df["STUDIENR"] == studienr
#
#     # Iterate through the rows and update "total_pr" based on prerequisites for the current "STUDIENR"
#     for index, row in df[mask].iterrows():
#         kurskode = str(row["KURSKODE"])
#         if kurskode in prerequisite_courses:
#             prerequisites = prerequisite_courses[kurskode]
#             pr = 0
#             grade = 0
#             for prereq_kurskode in prerequisites:
#                 prereq_kurskode = int(prereq_kurskode)
#                 for i, child in df[mask].iterrows():
#                     if child["KURSKODE"] == prereq_kurskode:
#                         pr += 1
#                         grade = grade + child['BEDOMMELSE']
#             df.at[index, "total_pr"] = pr
#             df.at[index, "total_pr_BEDOMMELSE"] = grade
#
# print(df)
#

import pandas as pd

# Your existing dataframe
data = {
    "STUDIENR": ["STNR000001", "STNR000001", "STNR000001", "STNR000001", "STNR000001", "STNR000002"],
    "KURSKODE": [2402, 28213, 41632, 41656, 41661, 28213],
    "KURSTXT": [
        "2402 Introduktion til statistik",
        "28213 Polymerteknologi",
        "41632 Robust design af produkter og mekanismer",
        "41656 Materialer i avancerede anvendelser og p...",
        "41661 Metallære",
        "2402 Introduktion til statistik",
    ],
    "BEDOMMELSE": [4.0, 7.0, 7.0, 10.0, 10.0, 9.0],
    "ECTS": [5.0, 5.0, 5.0, 10.0, 5.0, 5.0],
    "BEDOMMELSESDATO": [
        "2018-12-19",
        "2019-12-30",
        "2019-06-07",
        "2020-05-27",
        "2018-12-18",
        "2018-12-19",
    ],
}

df = pd.DataFrame(data)

# Prerequisite courses dictionary
prerequisite_courses = {
    "2402": ["28213", "41656"],
    "41656": ["41661"]
}

# Convert KURSKODE to string for consistent comparison
df['KURSKODE'] = df['KURSKODE'].astype(str)

# Add a new column "total_pr" to the dataframe
df["total_pr"] = 0
df["total_pr_BEDOMMELSE"] = 0

# Iterate through the rows and update "total_pr" based on prerequisites
for index, row in df.iterrows():
    kurskode = row["KURSKODE"]
    if kurskode in prerequisite_courses:
        prerequisites = prerequisite_courses[kurskode]
        pr = df[(df["STUDIENR"] == row["STUDIENR"]) & (df["KURSKODE"].isin(prerequisites))]
        df.at[index, "total_pr"] = len(pr)
        df.at[index, "total_pr_BEDOMMELSE"] = pr['BEDOMMELSE'].sum()

print(df)

