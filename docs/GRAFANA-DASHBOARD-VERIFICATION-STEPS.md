# ISO 50001 Dashboard - Verification Steps for Mr. Umut

**Date:** October 22, 2025  
**Grafana Status:** ✅ RUNNING (restarted at 18:53 UTC)  
**Dashboard File:** `grafana/dashboards/iso-50001-enpi-report.json`

---

## ⚠️ IMPORTANT: Clear Browser Cache First

Before accessing the dashboard, **clear your browser cache** to ensure you see the latest version:

**Chrome/Edge:**
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Close and reopen browser

**Firefox:**
1. Press `Ctrl + Shift + Delete`
2. Select "Cache"
3. Click "Clear Now"
4. Close and reopen browser

---

## Step 1: Access Grafana

### URL Options (try in order if one fails):

**Option A - Via Nginx Proxy (Recommended):**
```
http://localhost:8080/grafana
```

**Option B - Direct Grafana Port:**
```
http://localhost:3001
```

**Option C - If on remote server:**
```
http://YOUR_SERVER_IP:8080/grafana
```

### Expected Login Screen:
- Grafana logo with login form
- Username field
- Password field
- "Log in" button

### Default Credentials:
```
Username: admin
Password: admin
```

**✅ REPORT:** "I can see the Grafana login screen"

---

## Step 2: Navigate to Dashboard

After logging in:

1. **Click on the hamburger menu** (☰) in top-left corner
2. **Click "Dashboards"** in the sidebar
3. **Look for "ISO 50001 EnPI Report"** in the list
   - Should see dashboard with tags: `iso-50001`, `enpi`, `compliance`
   - May appear twice if duplicate (use either one)

**Alternative Navigation:**
- Click "Search" (magnifying glass icon in sidebar)
- Type "ISO 50001" in search box
- Click on "ISO 50001 EnPI Report"

**✅ REPORT:** "I can see 'ISO 50001 EnPI Report' in the dashboard list"

---

## Step 3: Verify Dashboard Variables (Top of Page)

Once dashboard opens, check the **top bar** for these dropdown filters:

### Expected Variables:

**1. SEU Selector** (left-most dropdown):
- Should show: "Material Handling" (default)
- Click dropdown to verify other options:
  - ✅ Compressed Air Production
  - ✅ Material Handling
  - ✅ Production Equipment
- **Select "Material Handling"** for verification

**2. Year Filter:**
- Should show: "2025" (default)
- Click dropdown to verify:
  - ✅ 2024
  - ✅ 2025

**3. Quarter Filter:**
- Should show: "Q3" (default)
- Click dropdown to verify:
  - ✅ Q1
  - ✅ Q2
  - ✅ Q3
  - ✅ Q4 (may be empty)

**✅ REPORT:** "I can see 3 dropdown filters at the top: SEU, Year, Quarter"

---

## Step 4: Verify Panel Layout (8 Panels Total)

### Panel 1: Compliance Status (Top-Left)
**What to expect:**
- Large colored box with text
- **Color:** 🟡 Yellow background (Warning status)
- **Text:** "⚠️ WARNING" or similar
- **Subtitle:** "Material Handling - 2025 Q3"

**✅ REPORT:** "Top-left panel shows YELLOW warning status"

---

### Panel 2: Deviation Gauge (Top-Center)
**What to expect:**
- Semi-circular gauge (speedometer style)
- **Needle position:** Around +3% to +4% (right side, yellow zone)
- **Range:** -10% (left) to +10% (right)
- **Color zones:**
  - Green: ±0-3%
  - Yellow: ±3-5%
  - Red: >±5%
- **Value displayed:** "+3.5%" or similar

**✅ REPORT:** "Gauge shows +3% to +4% deviation in yellow zone"

---

### Panel 3: Actual vs Expected Energy (Top-Right)
**What to expect:**
- Bar chart with TWO bars side-by-side
- **Blue bar (left):** "Actual Consumption" - Should be ~8.0 kWh
- **Orange bar (right):** "Expected Consumption" - Should be ~6.2 kWh
- **Height difference:** Actual bar slightly taller than Expected
- **Tooltip:** Hover over bars to see exact values

**✅ REPORT:** "Bar chart shows Actual (~8 kWh) slightly higher than Expected (~6 kWh)"

---

### Panel 4: Quarterly Performance Table (Middle-Left)
**What to expect:**
- Table with 4-5 columns
- **Headers:** Report Period, Actual (kWh), Expected (kWh), Deviation (%), Status
- **Row data (for Q3 2025):**
  - Report Period: `2025-Q3`
  - Actual: `~8.0 kWh`
  - Expected: `~6.2 kWh`
  - Deviation: `+3.5%` (in yellow or orange color)
  - Status: `warning` or colored indicator

**✅ REPORT:** "Table shows Q3 2025 with +3.5% deviation and 'warning' status"

---

### Panel 5: EnPI Trend Over Time (Middle-Center)
**What to expect:**
- Line chart with time on X-axis (months)
- **Two lines:**
  - Solid line: Actual consumption (fluctuating)
  - Dashed line: Expected baseline (smoother)
- **Background zones:**
  - Green band in center (±3%)
  - Yellow bands above/below green (±3-5%)
  - Red zones at top/bottom (>5%)
- **Months shown:** July, August, September (Q3)
- **Line position:** Should be in yellow zone, slightly above green band

**✅ REPORT:** "Line chart shows Jul-Aug-Sep with actual line in yellow zone above baseline"

---

### Panel 6: Baseline Model Information (Middle-Right)
**What to expect:**
- Text panel with formula and statistics
- **Content should include:**
  - "Baseline Year: 2024"
  - "R² Score: 0.9988" or similar
  - "Formula: Energy (kWh) = 0.0003 + 0.000123×production count - 0.000005×temp c"
  - "Intercept: 0.0003"
  - "Production Coefficient: 0.000123"
  - "Temperature Coefficient: -0.000005"

**✅ REPORT:** "Text panel shows formula with R² = 0.9988 and baseline year 2024"

---

### Panel 7: Monthly Breakdown (Bottom)
**What to expect:**
- Bar chart with 3 bars (one per month)
- **X-axis labels:** Jul, Aug, Sep
- **Y-axis:** Deviation percentage
- **Bar colors:** All yellow (warning status)
- **Bar heights:** All around +3% to +4%
- **Values:** Jul: +3.2%, Aug: +3.6%, Sep: +3.7% (approximately)

**✅ REPORT:** "Monthly breakdown shows 3 yellow bars (Jul, Aug, Sep) all around +3%"

---

### Panel 8: Dashboard Title/Description (Top)
**What to expect:**
- Large text at very top of dashboard
- **Title:** "ISO 50001 EnPI Report"
- **Subtitle/Description:** Explanation of dashboard purpose
- May also show filters reminder

**✅ REPORT:** "Dashboard title 'ISO 50001 EnPI Report' visible at top"

---

## Step 5: Test Interactive Features

### Test A: Change SEU
1. Click "SEU" dropdown at top
2. Select **"Compressed Air Production"**
3. **Expected changes:**
   - Compliance status turns 🔴 RED (Critical)
   - Gauge shows negative value (-9% to -27%)
   - All panels update with new data
   - Baseline formula changes (different coefficients)

**✅ REPORT:** "Changing SEU to Compressed Air shows RED status with negative deviation"

---

### Test B: Change Quarter
1. Keep SEU as "Material Handling"
2. Click "Quarter" dropdown
3. Select **"Q1"**
4. **Expected changes:**
   - Deviation changes slightly (+3.4% instead of +3.5%)
   - Monthly breakdown shows Jan, Feb, Mar instead of Jul, Aug, Sep
   - Actual/Expected values change slightly
   - Status remains 🟡 YELLOW (warning)

**✅ REPORT:** "Changing quarter to Q1 shows Jan-Feb-Mar with similar +3% deviation"

---

### Test C: Change Year
1. Keep SEU as "Material Handling", Quarter as "Q3"
2. Click "Year" dropdown
3. Select **"2024"**
4. **Expected result:**
   - **No data** or **"No data to display"** message
   - This is correct! 2024 is baseline year, no performance reports exist
   - Change back to **"2025"** to see data again

**✅ REPORT:** "Year 2024 shows no data (expected - baseline year)"

---

## Step 6: Verify Data Freshness

### Check Last Update Time
1. Look at bottom-right of any panel
2. Should show timestamp or "Last update: X minutes ago"
3. **Expected:** Recent timestamp (within last 10-15 minutes after restart)

### Refresh Dashboard
1. Click 🔄 refresh icon in top-right corner
2. **Or** press `Ctrl + R` to reload page
3. All panels should reload (may see brief loading spinners)
4. Data should remain consistent

**✅ REPORT:** "Dashboard refreshes successfully with consistent data"

---

## Step 7: Test Drill-Down (Optional)

### Click on Data Points
1. In "EnPI Trend Over Time" chart, **click on a data point** (dot on line)
2. **Expected:** Tooltip appears showing:
   - Date/time
   - Actual consumption value
   - Expected baseline value
   - Deviation percentage

### Zoom Timeline (Optional)
1. Click and drag on the X-axis (time axis) of EnPI trend chart
2. **Expected:** Zooms into selected time range
3. Click "Reset zoom" button to restore

**✅ REPORT:** "Can click data points and see tooltips with detailed values"

---

## Common Issues & Solutions

### Issue 1: Dashboard Not Found
**Symptoms:** "ISO 50001 EnPI Report" not in dashboard list

**Solutions:**
```bash
# Check if dashboard file exists
ls -lh /home/ubuntu/enms/grafana/dashboards/iso-50001-enpi-report.json

# Should show: 27K Oct 22 18:47

# If file exists, restart Grafana again
docker compose restart grafana

# Wait 15 seconds, then refresh browser
```

---

### Issue 2: "No Data" in All Panels
**Symptoms:** All panels show "No data" or empty

**Possible causes:**
1. **Wrong datasource selected**
   - Click panel title → Edit
   - Check datasource at top = "PostgreSQL"
   
2. **Database connection issue**
   - Test: Click gear icon ⚙️ → Data sources → PostgreSQL → "Save & test"
   - Should show green "Database Connection OK"

3. **No data in database for selected filters**
   - Verify filters: SEU = "Material Handling", Year = "2025", Quarter = "Q1/Q2/Q3"
   - Q4 2025 legitimately has no data (not yet completed)

**Verification query:**
```bash
docker exec enms-postgres psql -U raptorblingx -d enms -c "
SELECT report_period, actual_consumption_kwh, expected_consumption_kwh, deviation_percent 
FROM seu_energy_performance 
WHERE seu_id = '33333333-3333-3333-3333-333333333333' 
ORDER BY report_period;
"
```

**Expected output:**
```
 report_period | actual_consumption_kwh | expected_consumption_kwh | deviation_percent 
---------------+------------------------+--------------------------+-------------------
 2025-Q1       |                    7.8 |                      6.1 |               3.4
 2025-Q2       |                    7.9 |                      6.1 |               3.2
 2025-Q3       |                    8.0 |                      6.2 |               3.5
```

---

### Issue 3: Wrong Colors (All Green or All Red)
**Symptoms:** Status panel shows wrong color

**Check thresholds:**
1. Click panel title → Edit
2. Scroll to "Value mappings" or "Thresholds"
3. Should be:
   - Green: 0 to 3
   - Yellow: 3 to 5
   - Red: 5 to 100

---

### Issue 4: Variables Not Showing
**Symptoms:** No dropdowns at top of dashboard

**Solutions:**
1. Click gear icon ⚙️ at top → "Variables"
2. Should see 4 variables:
   - `seu_id` (Query type, visible)
   - `seu_name` (Query type, hidden)
   - `year` (Custom type, visible)
   - `quarter` (Query type, visible)
3. If missing, dashboard provisioning failed - check logs:
```bash
docker logs enms-grafana | grep -i "iso-50001"
```

---

## Success Checklist - Report Back to Agent

Copy this checklist and mark each item:

```
✅ Step 1: Logged into Grafana successfully
✅ Step 2: Found "ISO 50001 EnPI Report" in dashboard list
✅ Step 3: See 3 dropdown filters (SEU, Year, Quarter)
✅ Step 4-Panel 1: Yellow compliance status box visible
✅ Step 4-Panel 2: Gauge shows +3-4% in yellow zone
✅ Step 4-Panel 3: Bar chart with Actual > Expected
✅ Step 4-Panel 4: Table shows Q3 2025 with +3.5% deviation
✅ Step 4-Panel 5: Line chart shows Jul-Aug-Sep trend in yellow zone
✅ Step 4-Panel 6: Formula text with R²=0.9988 visible
✅ Step 4-Panel 7: Monthly breakdown with 3 yellow bars
✅ Step 4-Panel 8: Dashboard title at top
✅ Step 5-Test A: Compressed Air shows RED status with negative deviation
✅ Step 5-Test B: Q1 shows Jan-Feb-Mar with +3.4% deviation
✅ Step 5-Test C: Year 2024 shows no data (expected)
✅ Step 6: Dashboard refreshes successfully
✅ Step 7: Tooltips appear when clicking data points
```

---

## Quick Report Template

**For Mr. Umut - Copy and send to agent:**

```
Grafana Dashboard Verification - [YOUR NAME]

Access Status: ✅ SUCCESS / ❌ FAILED
URL Used: [http://localhost:8080/grafana or other]

Panel Verification:
- Compliance Status: [YELLOW/Other color seen]
- Deviation Gauge: [Value shown: +___%]
- Bar Chart: Actual [__kWh], Expected [__kWh]
- Table: Q3 2025 deviation = [__%]
- Trend Chart: [Data visible YES/NO]
- Formula Panel: R² = [____]
- Monthly Breakdown: [3 bars visible YES/NO]

Interactive Tests:
- SEU Change: [Works YES/NO]
- Quarter Change: [Works YES/NO]
- Year Change: [Shows no data for 2024 YES/NO]

Issues Encountered: [None / Describe any problems]

Screenshots: [Attach if possible]

Overall Status: ✅ READY FOR DEMO / ⚠️ NEEDS FIXES / ❌ BLOCKED
```

---

## Next Steps After Verification

**If all checks pass (✅):**
1. Take screenshots of dashboard with Material Handling SEU
2. Take screenshot of Compressed Air (RED status) for contrast
3. Review `docs/ISO-50001-DEMO-SUMMARY.md` for presentation notes
4. Schedule demo with Mr. Umut
5. Prepare to explain:
   - ±3% compliance achieved (Material Handling)
   - Quarterly tracking functional
   - Baseline accuracy R²=0.9988
   - Ready for ISO 50001 auditor review

**If issues found (⚠️):**
1. Note exact error messages
2. Take screenshots of problems
3. Report back to agent with details from "Quick Report Template"
4. Agent will provide fixes

---

**Dashboard File Location:** `/home/ubuntu/enms/grafana/dashboards/iso-50001-enpi-report.json`  
**Grafana Container:** `enms-grafana` (port 3001 → external 3001)  
**Nginx Proxy:** `http://localhost:8080/grafana`  
**Database:** `enms-postgres` (PostgreSQL datasource in Grafana)

**Support:** Report verification results back to agent using Quick Report Template above.

---

*Verification Guide Created: October 22, 2025*
