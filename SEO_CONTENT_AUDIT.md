# Publication.today — SEO content audit
**Audit date:** 2026-11-02  
**Scope:** 57 article records in `data/articles.json`, section pages, sitemap generator, sitemap output, and a sample of rendered article HTML. Search performance is based on finalized Google Search Console web data for 2026-08-01 through 2026-10-30.

## Executive diagnosis
The immediate issue is not a single technical indexing switch. The site has a very broad editorial footprint, little demonstrated organic demand, uneven article depth, and several time-sensitive pages that require active maintenance. The sitemap also contained a generic placeholder section page. That placeholder has been removed from the sitemap and from the generator's core-page list in this change.

## Inventory
| Category | Articles |
|---|---:|
| Fitness | 11 |
| Health | 10 |
| Wellness | 9 |
| Nutrition | 8 |
| Football | 6 |
| Skincare | 6 |
| Beauty | 4 |
| Technology | 3 |
| **Total** | **57** |

## Search Console signal
The page-dimension report exposed four rows for the audit period:
- HTTPS homepage: 3 impressions, 0 clicks.
- HTTP homepage: 1 impression, 0 clicks.
- Beginner home workouts: 1 impression, 0 clicks, average position 80.
- Champions League October results: 2 impressions, 0 clicks, average position 5.5.

These are the exposed rows, not proof that no other impressions occurred: Google can withhold low-volume/anonymized data. The HTTP/HTTPS homepage split should be checked at the live redirect/canonical layer. The Champions League result page is the strongest observed page-level signal, but it is a short-lived news query and not sufficient evidence to build the whole publication around football news.

## Technical findings and action
### Fixed in this change
- Removed `https://publication.today/section.html` from `scripts/generate-sitemap.py` and the current `sitemap.xml`. It is a generic “Explore a section / Loading stories…” template, not a useful landing page.
- Kept the file itself untouched to avoid breaking any legacy inbound links. If it is later retired, first verify it has no backlinks or external traffic, then redirect it to the most relevant section or return a proper 404/410.

### Already completed immediately before this audit
- Rebuilt `section-technology.html` as a crawlable static collection page with descriptive metadata, CollectionPage schema, and direct article links (PR #15).

## Editorial strategy
The current eight-category model dilutes topical authority. Do not publish more unrelated general-interest articles while the site is still trying to establish relevance. The best near-term test is **football utility and supporter tools**, not generic football news:
- Match-time conversion, countdowns and a 2027 competition calendar are concrete utilities with clear user tasks.
- The existing football fitness/recovery/nutrition content can support a narrower “football performance for recreational players” subcluster, but it should not be mixed indiscriminately with fixture news.
- Technology has only three articles. It could be a separate future vertical, but current GSC evidence is insufficient to justify prioritizing it over the existing football signal.
- Health, nutrition and skincare include YMYL topics and should not be expanded without named qualified reviewers, authoritative references, careful sourcing and substantive original value.

## Article-level priorities
### P1 — fact-check and maintain before further promotion
1. `google-gemini-4-argon-ai-model-coding-benchmark-pricing.html`: verify the model name, official release status, benchmark claims, context window, API availability and prices against primary Google documentation. Remove or clearly label unsupported claims; do not present speculative product claims as confirmed.
2. `champions-league-fixtures-week-barcelona-psg-real-madrid-leipzig-october-2026.html`: preserve as a dated match report, but ensure its headline and intro remain clearly historical and add links to current competition coverage. Do not keep targeting “fixtures this week” after the event has passed.
3. `el-clasico-preview-barcelona-vs-real-madrid-october-25-2026.html`: update the page to a clearly dated preview/recap or leave it as historical coverage; do not leave expired preview language implying the match is upcoming.
4. `champions-league-matchday-4-preview-barcelona-aston-villa-real-madrid-aek-november-2026.html` and `football-competitions-calendar-2027-afcon-womens-world-cup-champions-league.html`: verify all fixtures, dates, venues and organizer links against UEFA, CAF and FIFA before publication and whenever schedules change.

### P2 — strengthen useful evergreen assets
- `ai-automation-roi-calculator.html`: protect as a differentiated tool. Add a worked example, assumptions/methodology, limitations, and a clear explanation of what “payback” means.
- `walking-calories-calculator.html`, `daily-protein-intake-calculator.html`, `daily-calorie-needs-calculator.html`, `bmi-calculator.html`, `sleep-calculator-bedtime.html`: keep the calculator pages only if the tool works reliably, formulas are transparent, units/accessibility are tested, and supporting content answers real user questions. Health-related calculators need clear limits and authoritative citations.
- `football-match-time-zone-converter.html` and `football-match-countdown.html`: make the tool pages more useful with tested examples, timezone edge cases, fixture verification instructions and links from every relevant football guide.

### P3 — consolidate overlapping informational topics
Review overlaps before merging; do not delete or noindex pages solely because they are short:
- Fitness: `build-a-fitness-routine-that-lasts`, `beginner-guide-to-home-workouts`, `strength-training-beginners`, `choosing-cardio-you-enjoy`, `walking-for-everyday-fitness`.
- Health/wellness: `building-a-healthier-morning`, `mindful-mornings-without-perfection`, `habit-stacking-explained`, `healthy-habits-on-a-tight-budget`.
- Nutrition: `balanced-plate-basics`, `protein-basics-for-everyday-eating`, `daily-protein-intake-calculator`, `football-match-day-nutrition-guide`.
- Skincare/beauty: `simple-skincare-routine`, `beauty-routine-edit`, `oily-skin-moisturizer`, `what-skin-barrier-means`, `exfoliation-how-much-is-enough`.

## Evidence limits
- The inventory count and category split come from the complete 57-record article feed.
- Rendered HTML depth was sampled across representative articles; it ranged from roughly 266 visible words for the blood-pressure guide to about 1,015 for the Gemini/Argon article and 614 for the 2027 AI trends guide. This sample is not a full 57-page word-count audit.
- Low impressions do not prove that Google rejected the site. They indicate that Google currently exposes very little search visibility for the selected period.
- No article has been deleted, merged, or noindexed as part of this audit.

## Next 30-day execution order
1. Verify the HTTP-to-HTTPS redirect and canonical consistency, then re-submit the corrected sitemap in Search Console.
2. Fact-check the four time-sensitive/high-risk articles listed under P1.
3. Improve the football section as a coherent utility hub and add contextual internal links among the three football tools and the 2027 calendar.
4. Rewrite only the highest-value evergreen pages with original examples, authoritative citations, clear author/reviewer information and useful FAQs.
5. Reassess GSC page/query data after 28 days; expand only the cluster that earns impressions and engagement.
