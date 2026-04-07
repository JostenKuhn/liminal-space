#!/usr/bin/env python3
"""Liminal Space — Analytics Dashboard
Pull GA4 + Beehiiv data in one shot.
Usage: python3 analytics.py [days]  (default: 7)
"""

import os, sys, json, requests
from datetime import datetime

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/tarynlee/Desktop/gms-agent/finance_dashboard/service_account.json'

PROPERTY_ID = "530250394"
BEEHIIV_KEY = "vGBSFR9R5CV9pObcj1wIATBHoQfkzvodApBf2NnEG5KuQXKlTkaGDi4ccjCd6BNe"
BEEHIIV_PUB = "pub_a3a0d9b3-87df-485b-a288-791359f96519"

days = int(sys.argv[1]) if len(sys.argv) > 1 else 7

# ── GA4 ──────────────────────────────────────────────
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension, OrderBy

client = BetaAnalyticsDataClient()

print(f"\n{'='*60}")
print(f"  LIMINAL SPACE — ANALYTICS ({days} days)")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}")

# Overview
r = client.run_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
    metrics=[
        Metric(name="activeUsers"),
        Metric(name="sessions"),
        Metric(name="screenPageViews"),
        Metric(name="averageSessionDuration"),
        Metric(name="bounceRate"),
        Metric(name="eventCount"),
    ],
))
if r.rows:
    row = r.rows[0]
    print(f"\n📊 OVERVIEW")
    print(f"  Users:           {row.metric_values[0].value}")
    print(f"  Sessions:        {row.metric_values[1].value}")
    print(f"  Page views:      {row.metric_values[2].value}")
    print(f"  Avg session:     {float(row.metric_values[3].value):.0f}s")
    print(f"  Bounce rate:     {float(row.metric_values[4].value):.1%}")
    print(f"  Total events:    {row.metric_values[5].value}")

# Pages
r2 = client.run_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
    dimensions=[Dimension(name="pagePath")],
    metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
))
print(f"\n📄 PAGES")
for row in r2.rows:
    print(f"  {row.dimension_values[0].value:40s} | {row.metric_values[0].value:>5s} views | {row.metric_values[1].value:>4s} users")

# Traffic sources
r3 = client.run_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
    dimensions=[Dimension(name="sessionSource")],
    metrics=[Metric(name="sessions"), Metric(name="activeUsers")],
))
print(f"\n🔗 TRAFFIC SOURCES")
for row in r3.rows:
    print(f"  {row.dimension_values[0].value:30s} | {row.metric_values[0].value:>5s} sessions | {row.metric_values[1].value:>4s} users")

# Daily breakdown
r4 = client.run_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="activeUsers"), Metric(name="sessions"), Metric(name="screenPageViews")],
    order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
))
print(f"\n📅 DAILY")
for row in r4.rows:
    d = row.dimension_values[0].value
    print(f"  {d[0:4]}-{d[4:6]}-{d[6:8]} | {row.metric_values[0].value:>4s} users | {row.metric_values[1].value:>5s} sessions | {row.metric_values[2].value:>5s} views")

# Device breakdown
r5 = client.run_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
    dimensions=[Dimension(name="deviceCategory")],
    metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
))
print(f"\n📱 DEVICES")
for row in r5.rows:
    print(f"  {row.dimension_values[0].value:15s} | {row.metric_values[0].value:>4s} users | {row.metric_values[1].value:>5s} sessions")

# Country breakdown
r6 = client.run_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
    dimensions=[Dimension(name="country")],
    metrics=[Metric(name="activeUsers")],
))
print(f"\n🌍 COUNTRIES")
for row in r6.rows:
    print(f"  {row.dimension_values[0].value:25s} | {row.metric_values[0].value:>4s} users")

# ── BEEHIIV ──────────────────────────────────────────
print(f"\n📧 BEEHIIV SUBSCRIBERS")
resp = requests.get(
    f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB}/subscriptions?limit=100&order_by=latest",
    headers={"Authorization": f"Bearer {BEEHIIV_KEY}"}
)
subs = resp.json()["data"]
active = [s for s in subs if s["status"] == "active"]
print(f"  Total: {len(subs)}  |  Active: {len(active)}")
print(f"\n  Latest signups:")
for s in subs[:10]:
    dt = datetime.fromtimestamp(s["created"]).strftime("%b %d %H:%M")
    src = s.get("utm_source", "") or "direct"
    print(f"    {s['email']:35s} | {dt} | {s['status']:8s} | {src}")

print(f"\n{'='*60}")
print(f"  Run: python3 analytics.py 30  (for 30-day report)")
print(f"{'='*60}\n")
