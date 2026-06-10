import pandas as pd

file_path = r"C:\Users\Administrator\Desktop\Projects\SEO and AI automation\Data\raw\JYPRA keyword volume and bidding(Keyword Strategy).csv"

# Header is row 2 (third row)
df = pd.read_csv(
    file_path,
    encoding="cp1252",
    header=2
)

# Clean column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace("\n", "_")
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")
)

print("\nColumns:")
print(df.columns.tolist())

print("\nTotal Keywords:", len(df))

print("\nTop 10 Keywords:")
print(df[['keyword', 'avg_monthly_searches']].head(10))

#Bulid Opportunities finder

df['avg_monthly_searches'] = pd.to_numeric(
    df['avg_monthly_searches'],
    errors='coerce'
)

# High-volume keywords
opportunities = df.sort_values(
    by='avg_monthly_searches',
    ascending=False
)

print("\nTop Opportunities")
print(
    opportunities[
        ['keyword', 'avg_monthly_searches', 'competition']
    ].head(10)
)
#Categorize Keywords Automatically
def categorize_keyword(keyword):
    keyword = str(keyword).lower()

    if "penetration" in keyword or "pentest" in keyword:
        return "Penetration Testing"

    elif "cloud" in keyword:
        return "Cloud Security"

    elif "network" in keyword:
        return "Network Security"

    elif "managed" in keyword:
        return "Managed Security"

    elif "assessment" in keyword:
        return "Security Assessment"

    elif "consulting" in keyword:
        return "Security Advisory"

    else:
        return "Cyber Security"


df["category"] = df["keyword"].apply(categorize_keyword)

print(df[["keyword", "category"]].head(10))

#Create the Keyword opporunites Score
df["opportunity_score"] = (
    df["avg_monthly_searches"] *
    df["rankability_score_1–5"]
)

top_keywords = df.sort_values(
    by="opportunity_score",
    ascending=False
)

print(
    top_keywords[
        ["keyword",
         "avg_monthly_searches",
         "rankability_score_1–5",
         "opportunity_score"]
    ].head(10)
)

#Export Results to Excel
output_file = r"..\outputs\keyword_opportunities.csv"

top_keywords.to_csv(
    output_file,
    index=False
)

print(f"Saved: {output_file}")

#Final report
final_report = top_keywords[
    [
        "keyword",
        "category",
        "avg_monthly_searches",
        "competition",
        "rankability_score_1–5",
        "opportunity_score"
    ]
]

final_report.to_csv(
    r"..\outputs\keyword_opportunities.csv",
    index=False
)

print("Keyword Report Generated Successfully")

