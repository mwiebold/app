# Initial Beestat review

Reviewed 2026-11-02 against upstream `22db006` (2026-10-23). Scope: repository
setup, architecture and chart paths, local boot checks, public demo inspection,
and current upstream issue inventory. This is not a full security audit or a
validation of the scientific models against real thermostat data.

## What is here

The app is an actively maintained PHP/MySQL monolith with a custom JavaScript
component system. It has no React/Vue build, npm manifest, or Composer manifest.
Libraries are vendored in `js/lib/`: Highcharts 11.4.3, Moment, Rocket, Three.js,
and supporting geometry libraries. The repository carries GPL-3.0 and the
vendored libraries retain their own notices.

| Area | Existing behavior | Main files |
| --- | --- | --- |
| Detail | Indoor/outdoor temperature, humidity, setpoints, HVAC runtime lanes; sensor temperature and occupancy | `js/layer/detail.js`, `js/component/card/runtime_*_detail.js`, `js/component/chart/runtime_*_detail_*.js` |
| Analyze | Runtime summaries by period, outdoor temperature and degree days; raw temperature profiles and fitted trends for heating/cooling stages and passive drift | `js/layer/analyze.js`, `js/component/card/runtime_thermostat_summary.js`, `js/component/card/temperature_profiles.js` |
| Compare | Home/system metrics, runtime per degree day, balance points and peer comparisons | `js/layer/compare.js`, `js/component/metric/`, `js/beestat/comparisons.js` |
| Air quality | Air-quality score, VOC and CO2 plots for supporting sensors | `js/layer/air_quality.js`, `js/component/chart/air_quality.js`, `voc_concentration.js`, `co2_concentration.js` |
| Visualize | Floor-plan editor and 3D interior/exterior environment | `js/layer/visualize.js`, `js/component/scene/`, `js/component/floor_plan*` |
| Export | Data downloads and local PNG chart exports | `api/runtime.php`, `js/component/modal/download_data.js`, `js/component/chart.js` |

## Data and rendering flow

1. `api/ecobee*.php` handles OAuth and remote thermostat/sensor metadata.
2. `api/runtime.php` imports five-minute runtime/sensor history. Raw temperature
   values are stored in tenths of degrees Fahrenheit; runtime values are seconds.
3. `api/runtime_thermostat_summary.php` produces daily aggregates;
   `api/profile.php` builds thermal profiles and derived performance metrics.
4. `api/cora/` supplies the API dispatcher, session checks, CRUD, transactions,
   caching, and logging. Most user resources require a session and user scope.
5. `js/layer/load.js` loads data into `beestat.cache`; cards prepare plot series.
   `js/component/chart.js` centralizes Highcharts defaults, rendering, and export.
6. `js/js.php` lists scripts in dependency order in development mode. A new card
   or chart must be registered there and mounted in the relevant layer.

## Findings that affect new features

1. **Fresh schema import was broken.** `api/beestat.sql` had a trailing comma
   after the `api_user` unique key. This fork removes it. The corrected schema
   imported into a fresh MySQL 8.4 volume with all 32 tables and two local API users.
2. **A local backend is not yet a connected dashboard.** The Docker setup works,
   but OAuth still requires the existing ecobee app's callback and an HTTPS
   hostname. `index.php` hard-codes HTTPS for the login redirect; the public demo
   also assumes `demo.beestat.io`. There is no checked-in sample dataset.
3. **The upstream checkout has no automated tests or CI workflows.** It contains
   an ESLint configuration, but no pinned ESLint dependency or runnable lint
   command. This fork adds source syntax and HTTP/API smoke checks only.
   New calculations need numerical tests covering missing samples, units,
   thermostat timezone/DST, and staging behavior.
4. **Production packaging is not reproducible from this checkout alone.**
   `js/js.php` loads individual files in `dev`/`dev_live`, but otherwise expects
   the main `js/beestat.js` to contain the built application. No build command
   or bundler configuration is checked in. Stay in `dev` until packaging is added.
5. **Data coverage needs to be visible in future plots.** Summary gap filling
   extrapolates from available samples (`gap_fill_` uses 288 samples per day).
   Missing-data, timezone, and unit behavior should be tested before deriving
   efficiency or cost conclusions. The raw thermostat API limits reads to about
   31 days, so long-range plots should use summaries or deliberate chunking.
6. **Peer comparisons need peer data.** An isolated instance starts empty and
   cannot reproduce the hosted service's comparison population from its own
   thermostat history alone.

GitHub reported **30 open issues and 0 open pull requests** at review time.
Relevant existing reports include [missing-data gap fill](https://github.com/beestat/app/issues/379),
[temperature profile unit conversion](https://github.com/beestat/app/issues/386),
[empty sensor loading](https://github.com/beestat/app/issues/350), and
[multi-section chart exports](https://github.com/beestat/app/issues/235).
These are upstream reports, not bugs reproduced in this review. Issue titles
can be stale: for example, #401 requests an occupancy schema type already present
in the current SQL dump. Confirm each report before treating it as remaining work.

## Recommended next work

First connect the existing app through a correctly configured HTTPS callback,
or add a small deterministic sample dataset for offline chart development.
Then choose the first requested plot and implement it as a card/chart within
the existing Analyze or Detail layer. Reuse the unit, date-range, cache, and
Highcharts helpers; avoid a framework rewrite as a prerequisite.

Good candidates using existing data include runtime versus outdoor-temperature
scatter plots, daily/hourly runtime heatmaps, and room-to-room temperature spread.
Energy/cost plots need explicit power and tariff assumptions or measured energy
data; runtime alone is not measured kWh. These are candidates, not implemented
features or a committed feature scope.

## Validation baseline

- PHP 8.5/Apache and MySQL 8.4 containers start; fresh SQL import succeeds.
- 182 JavaScript files (181 application files plus the service worker) pass
  `node --check`; vendor files excluded.
- 54 PHP files pass syntax checks, including the generated local settings file.
- Public API read succeeds; a private user read without a session is rejected.
- Development files are denied over HTTP; application JavaScript is served.
- Setup generation, preservation of existing settings, and rejection of a
  changed settings template were checked with temporary-directory assertions.
- Public demo loads the existing system/sensor dashboard.
- No live ecobee OAuth, real-account synchronization, numerical model accuracy,
  exhaustive browser chart interactions, or production deployment was tested.
