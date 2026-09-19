# Shipping Rate Estimator — Project Notes

## What this project does
Takes an SMS signup list, extracts each subscriber's area code as a proxy for
location, gets real USPS postage for each, and computes a signup-weighted
average shipping cost. The goal is to replace a guessed flat rate (e.g.
$8.99) with one grounded in where your actual customer base lives, so
checkout shipping cost stops being a surprise that kills conversion.

## Core assumption (name it, don't hide it)
The SMS list's geographic distribution is used as a stand-in for the actual
buyer distribution. This holds only as well as two things are true:
1. Area code approximates current location. It doesn't always — people keep
   old area codes after moving (mobile number portability). This is a known,
   acceptable limitation at drop-list scale, not a fatal flaw, but it should
   be stated plainly whenever this project is discussed (resume, interviews).
2. SMS subscribers resemble actual buyers. Some buyers won't be on the SMS
   list at all. If non-SMS buyers skew to different, pricier regions, the
   flat rate will run low. Because this is US + Canada only, the spread
   should be bounded, but it's an assumption worth checking, not assuming
   away.

**Follow-up validation (do this after the actual drop):** pull real order
addresses from Shopify and compare their distribution to what the SMS list
predicted. This closes the loop and is the strongest part of the project to
talk about afterward — it turns "I built a pricing tool" into "I built and
validated a pricing tool."

## Why weighted, not simple, average
Weight each area code's postage by its signup count, not by treating every
unique area code equally. Otherwise a handful of far-away signups get the
same influence as your biggest cluster of nearby customers.

Example: 415 (SF) x 80 signups at $6, 212 (NYC) x 20 signups at $9.
- Simple average of the two rates: $7.50
- Signup-weighted average: (80x6 + 20x9) / 100 = $6.60

The weighted number is the one that reflects your real customer base.

## The cross-subsidization question
A flat rate always means nearby customers pay a little more than their real
cost, to subsidize distant customers, in exchange for one simple number at
checkout instead of dozens. That's the tradeoff, not a flaw. What's worth
measuring is how much subsidy you're asking for:

- % of customers whose actual USPS quote is $1.50-2+ *below* the proposed
  flat rate (the ones subsidizing)
- % whose quote is $2+ *above* it
- standard deviation of the weighted distribution — small spread means the
  flat rate is a solid stand-in; large spread means one number is doing too
  much work and a tiered rate might be worth it

## Don't blend US and Canada without checking first
Canada shipping from a US origin usually costs meaningfully more (customs,
international mail class). If even a modest slice of the SMS list is
Canadian, a single blended average could sit noticeably above what most
(likely mostly domestic) customers would expect. Compute both:
- domestic-only weighted average
- full blended (US + Canada) weighted average

If they diverge a lot, the real recommendation may be two flat rates (US /
Canada) instead of one.

## Metrics to report for validation
1. Weighted average shipping cost vs. $8.99 (the original guess) and vs.
   $6.99 (the number under consideration for the next drop)
2. Domestic-only average vs. blended average
3. Spread: std dev, min, max of per-area-code postage
4. Overpay / underpay percentages at the $1.50-2 threshold above
5. (Post-drop) predicted distribution vs. actual order address distribution

## Resume framing (Google XYZ style, draft once numbers exist)
"Replaced a guessed flat shipping rate with a data-driven rate derived from
[N] SMS signups and live USPS postage lookups, reducing checkout shipping
cost variance by [X]% for the [drop name] launch."
Fill in the brackets once the pipeline has run on a real list — don't
estimate these numbers ahead of time.

## Open questions to settle before treating results as final
- Seller origin ZIP and package weight/dimensions (needed for USPS quotes)
- Whether to report one flat rate or a US/Canada split
- What overpay/underpay threshold actually matters for your customers —
  $1.50? $2? worth sanity-checking against the $6-8 tolerance you mentioned
