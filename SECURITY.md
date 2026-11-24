# Security policy

## Supported versions

Only the default branch (`main`) is supported. There are no releases or published packages.

## Reporting a vulnerability

Report it privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability** (private vulnerability reporting). Do not open a public issue for a vulnerability.

Include what you did, what you expected and what happened, and the commit you tested. The program is designed to write only inside its own workspace, to never follow a link or accept a path from the browser, and to unpack archives within fixed limits; reports that break those rules are the most useful. Only the scaffold exists and no product behaviour is implemented yet, so reports are about the plan in `docs/PROJECT-PLAN.md` until the first tickets land.
