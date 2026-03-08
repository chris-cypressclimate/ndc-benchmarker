from dash import dcc, html

def get_layout():
    return html.Div([
        html.H2("NOTES AND METHODS", className="section-header"),
        html.Div(className="explainer-text", children=[
            html.H3("Last updated", className="section-title"),
            dcc.Markdown("March 5, 2026"),

            html.H3("Count of countries with new NDCs", className="section-title"),
            dcc.Markdown("""
The total count of new Nationally Determined Contributions (NDCs) is for all countries that have submitted NDCs since January 1, 2024. This count includes the United States, which submitted an NDC in December 2024 before withdrawing from the Paris Agreement in January 2025. The count of countries also includes the 27 member states of the EU (but not the EU itself as a party). Countries that are parties to the [UN Framework Convention on Climate Change](https://unfccc.int/process-and-meetings/united-nations-framework-convention-on-climate-change) but have not ratified the [Paris Agreement](https://unfccc.int/process-and-meetings/the-paris-agreement) are also included (e.g., Yemen, which has [submitted](https://unfccc.int/sites/default/files/2025-11/Yemens%20NDC3.0%20Vision.pdf) an NDC "vision and framework”). Some of the new NDCs submitted by countries since 2024 do not contain targets for 2035 but are nevertheless counted here as being new NDCs.
            """),

            html.H3("Past emissions trends", className="section-title"),
            dcc.Markdown("""
Data on past greenhouse gas (GHG) emissions are sourced primarily from parties' national inventory data reported to the UN since 2024, including in [Biennial Update Reports](https://unfccc.int/BURs) (BURs), [Biennial Transparency Reports](https://unfccc.int/first-biennial-transparency-reports) (BTRs), formal [NDC submissions](https://unfccc.int/NDCREG), and Annex 1 parties' [National Inventory Reports](https://unfccc.int/ghg-inventories-annex-i-parties/2025) (NIRs). A compilation of all inventory data reported by parties since 2024 is available [here](https://docs.google.com/spreadsheets/d/1F9opy0QXEVw5lcrjhuymbmWczSiNsauY/edit?usp=sharing&ouid=107483244733420618943&rtpof=true&sd=true).

[PRIMAP-hist](https://zenodo.org/records/17090760) estimates of total emissions with and without [LULUCF](https://unfccc.int/topics/land-use/workstreams/land-use--land-use-change-and-forestry-lulucf) are used to fill gaps in the official national inventory data. Internal gaps in the inventory data are filled to mimic year-on-year variation in the ‘HISTCR’ series of the PRIMAP data. Interpolated estimates are rescaled to be consistent with official data in the years before and after those gaps. Estimates are also extrapolated for the earliest and most recent years where official data are missing. The PRIMAP data are only used to fill missing years of data where there is generally good agreement between the inventory data and PRIMAP hist estimates in years where the two overlap (i.e., within a range of 15% on average and never more than 25% in absolute terms). The PRIMAP data are used directly for countries with no inventory data reported for years after 2010, with a few exceptions.  To ensure consistency, the same data source is always used for total emissions with and without LULUCF for a given country and year.
            """),

            html.H3("NDC target ranges and trajectories", className="section-title"),
            dcc.Markdown("""
The illustrated NDC target ranges for 2030 and 2035 include both conditional and unconditional targets. For parties that have put forward targets for emissions reductions compared to a business-as-usual (BAU) trajectory, if the targets are entirely conditional, then the BAU scenario is taken as the upper end (unconditional portion) of the party's target.

2030 NDC target values have been updated for parties that have published new national inventory data for reference year emissions since they first announced their 2030 targets. Where applicable, target reference levels have also been updated to be consistent with each party's latest national inventory data (e.g., Japan's FY 2013 emissions levels shown in this data tool are as [reported](https://www.nies.go.jp/gio/en/aboutghg/index.html) by the Greenhouse Gas Inventory Office of Japan in April 2025 after Japan's NDC was released in February 2025).
            """),

            html.H3("Peak GHG emissions", className="section-title"),
            dcc.Markdown("""
Emissions peaks are evaluated for the post-1990 period only (the years covered by national inventory data reported to the UN). Structural peaks are identified as occurring where emissions reach a maximum and then trend downward, with no evidence of a statistically significant upward rebound in the years after peaking (e.g., following economic shocks such as the COVID-19 pandemic). Year-on-year percent changes in emissions pre- and post-peak are evaluated by piecewise linear regression using log-transformed emissions levels to compare year-on-year percent changes.  Secondary tests are performed using Spearman’s rank correlation.

Secondary peaks are also considered (e.g., for many former Soviet states that saw their emissions collapse in the early 1990s and then gradually recover). In the case of a secondary peak, emissions in the peak year must exceed those in the three years leading up to the peak and for all years after the peak. Emissions must also show a statistically significant increasing trend from their lowest point after 1990 leading up to the secondary peak, and then a statistically significant year-on-year decrease after the peak, with no further rebounding.

NDC targets for peak emissions are also incorporated. Where a party has set a peaking target in its latest NDC, the targeted peak year or peaking period is presented (regardless of whether the party’s actual emissions have already hit a structural before the target year).
            """),

            html.H3("Linear trajectories to net zero", className="section-title"),
            dcc.Markdown("""
A party’s 2035 NDC target is classified as representing a “credible” pathway to net zero if the implied average pace of emissions reductions leading up to 2035 to achieve a party's NDC would put it on track to reaching its net zero target over the longer term. In other words, the party’s 2035 target must represent a linear or steeper trajectory to net zero. [Projections](https://rhg.com/wp-content/uploads/2024/10/Rhodium-Climate-Outlook-2024_Probabilistic-Global-Emissions-and-Energy-Projections.pdf) by the Rhodium Group show that if major emitters followed a straight-line path from their 2030 NDCs to reach net zero GHG emissions by mid-century (and the remaining countries without existing net zero targets charted a pathway to realize net zero by 2070), overshoot of the Paris Agreement’s 1.5°C temperature goal would be limited and warming could be held to 1.1-1.7°C by century’s end (with a median estimate of 1.4°C).

Three types of linear-to-net-zero trajectories are considered, as illustrated in the figure below:

1. From peak emissions
2. From current emissions levels
3. From a party’s 2030 NDC
            """),
            html.Img(src='/assets/s2z_formulations.png', style={'maxWidth': '100%', 'height': 'auto', 'display': 'block', 'width': '500px'}),
            html.Br(),
            dcc.Markdown("""
Formulation (2) is only applied if a party has not already peaked its emissions **and** has not set a 2030 NDC target. Satisfying (2) represents a high bar for assessing the NDC targets of parties that have not yet peaked their emissions and suggests that a country will aim for a steeper-than-linear trajectory from its future emissions peak to net zero (see Thailand's NDC, for example). A party’s 2035 target is classified as being on a credible track to net zero if any part of its target range is on a linear-or-steeper trajectory. With formulation (3), however, the lower end of the party’s 2035 target range is only judged against the lower end of its 2030 target, and the upper end of its 2035 target is only compared against the upper end of its 2030 target.

Additional criteria apply. First, if a party has already peaked its emissions, its 2035 target should represent a decrease from its present-day emissions (see the Russian Federation, for example). Second, a party’s targeted peak year should be before 2035 (see Ecuador, for example).  Third, if a party already has net-negative emissions and aims to remain net negative by 2035, this is also categorized as being on a credible track.

For countries that have already submitted NDCs, the linear-to-net-zero benchmark for credibility is only assessed where parties have stated goals for reaching net zero and set 2035 targets to reduce their total emissions including LULUCF. NDC targets for gross emissions excluding LULUCF only cannot be judged against this benchmark.
            """),

            html.H3("IPCC and NGFS climate scenarios", className="section-title"),
            dcc.Markdown("""
[IPCC AR6](https://www.ipcc.ch/assessment-report/ar6/) climate scenario data are obtained from the [AR6 Scenario Explorer and Database](https://data.ene.iiasa.ac.at/ar6/#/login?redirect=%2Fworkspaces) hosted by the International Institute for Applied Systems Analysis (IIASA). Only economy-wide scenarios with ISO3-level projections that have passed vetting are included, yielding a sample of 1,059 scenarios for 13 countries/parties. Some integrated assessment models (e.g., MESSAGE and REMIND-MAgPIE) account for a disproportionate number of scenarios in the overall sample. Models are given equal weight in constructing the ranges for the 5th to 95th percentiles of scenarios so as to avoid individual models skewing the overall results. Weights are applied to individual scenarios according to the inverse of the total number of scenarios per model/study.

Downscaled [NGFS](https://www.ngfs.net/ngfs-scenarios-portal/) climate scenario data are obtained from the [NGFS Phase 5 Scenario Explorer](https://data.ene.iiasa.ac.at/ngfs/#/license) maintained by IIASA. The NGFS data include results for more individual countries/parties but from fewer models (GCAM, REMIND-MAgPIE, and MESSAGEix-GLOBIOM) compared with the IPCC data. Because of this, ranges are shown for the minimum and maximum 2035 emissions levels rather than the 5th to 95th percentiles.
            """),

            html.H3("License and permissions", className="section-title"),
            dcc.Markdown("""
Data and visualizations are provided under a [Creative Commons CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license, which allows unrestricted reuse with proper attribution. The dashboard may be cited as: **Chris Sall, “NDC Benchmarker” (2026), Cypress Climate Advisory, https://ndcbenchmarker.org/**.

Some of the underlying data sets featured in this dashboard may have different licenses or permissions. The dashboard provides links and citations for these underlying sources where available. Please refer to the original licensing and permissions for these data sets included in the list of sources below and cite them appropriately when referring to specific sections of this database.

The data compiled in this unofficial database are intended for general informational purposes only. No guarantees are made as to their completeness, accuracy, correctness, timeliness, or reliability.
            """),
        ]),

        html.H2("Sources", className="section-header"),
        html.Div(className="explainer-text", children=[
            dcc.Markdown("""
\\[1] “Climate Watch NDC Tracker.” 2025. Washington, DC: World Resources Institute. Available online at: https://www.climatewatchdata.org/ndc-tracker

\\[2] Cui, R.; Behrendt, J.; Borrero, M.A.; Bertram, C.; Nelson-Rowntree, X.; Hultman, N.; Lou, J.; Zhao, A.; Tibebu, T.B.; O'Keefe, K.; George, M.; Miller, A.; Schreier, M.; Li, X.; Kreis, A.; Churlyaev, D.; Syed, M. 2025. “Country Climate Ambition: High Ambition Pathways for National and Global Climate Goals.” Center for Global Sustainability, University of Maryland, http://www.country-ambition.cgs.umd.edu

\\[3] Gütschow, J.; Busch, D.; Pflüger, M. 2025. “The PRIMAP-hist national historical emissions time series v2.7 (1750-2024).” Zenodo, https://zenodo.org/records/17090760

\\[4] International Institute for Applied Systems Analysis (IIASA). 2022. “AR6 Scenarios Database,” https://data.ene.iiasa.ac.at/ar6/

\\[5] IIASA. 2024. “NGFS Phase 5 Scenario Explorer,” https://data.ene.iiasa.ac.at/ngfs/#/workspaces

\\[6] Larsen, K.; Mobir, M.; Movalia, S.; Pitt, H.; Rivera, A.; Rutkowski, E.; Tamba, M. 2024. “Rhodium Climate Outlook 2024: Probabilistic Global Emissions and Energy Projections.” Rhodium Group, New York, https://rhg.com/wp-content/uploads/2024/10/Rhodium-Climate-Outlook-2024_Probabilistic-Global-Emissions-and-Energy-Projections.pdf

\\[7] Network of Central Banks and Supervisors for Greening the Financial System (NGFS). 2024. “Scenarios Portal,” https://www.ngfs.net/ngfs-scenarios-portal/

\\[8] “Net Zero Tracker.” 2025. https://zerotracker.net/.

\\[9] Schmidt, J. 2025. "Countries Announce Continued Action on 2035 Climate Plans," Natural Resources Defense Council (NRDC), https://www.nrdc.org/bio/jake-schmidt/countries-announce-continued-action-2035-climate-plans#plans
            """)
        ])
    ], className="p-3")
