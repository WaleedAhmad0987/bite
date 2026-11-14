# What each function must do

- **discount**: codes `SAVE10` and `SAVE25` take 10% and 25% off, matched in any letter case. Orders under 50 get no discount. The discount is at most 40. A negative price or an unknown code is an error.
- **password**: strong means 12 characters or more, with an upper-case letter, a lower-case letter and a digit, and not on the common list in any letter case.
- **shipping**: a domestic (PK) parcel of 0.5 kg or less ships free unless it is express. Otherwise the cost is a base of 5 (domestic) or 20 (abroad) plus 2 per kg, and express costs 1.5 times that. Weight must be positive.
- **pagination**: pages start at 1, per_page is capped at 100, and a page past the end returns an empty range at the end.
- **refunds**: only the order's owner may refund, up to and including 30 days after the order, a positive amount, and never more than was paid in total.
