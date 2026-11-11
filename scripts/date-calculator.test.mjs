import test from "node:test";
import assert from "node:assert/strict";
import { calculateDateDifference, parseDateUTC } from "./date-calculator.mjs";

test("calculates elapsed days, weeks, and weekdays for the article example", () => {
  assert.deepEqual(calculateDateDifference("2026-11-11", "2026-12-19"), {
    days: 38,
    weeks: 5,
    remainingDays: 3,
    weekdays: 28,
  });
});

test("date order does not change the positive difference", () => {
  assert.deepEqual(
    calculateDateDifference("2026-12-19", "2026-11-11"),
    calculateDateDifference("2026-11-11", "2026-12-19"),
  );
});

test("same-day ranges return zero", () => {
  assert.deepEqual(calculateDateDifference("2026-11-11", "2026-11-11"), {
    days: 0,
    weeks: 0,
    remainingDays: 0,
    weekdays: 0,
  });
});

test("handles leap-day boundaries in UTC", () => {
  assert.deepEqual(calculateDateDifference("2024-02-28", "2024-03-01"), {
    days: 2,
    weeks: 0,
    remainingDays: 2,
    weekdays: 2,
  });
});

test("does not count weekend days as weekdays", () => {
  assert.equal(calculateDateDifference("2026-11-14", "2026-11-16").weekdays, 0);
});

test("rejects impossible and malformed calendar dates", () => {
  assert.throws(() => parseDateUTC("2026-02-30"), RangeError);
  assert.throws(() => parseDateUTC("not-a-date"), RangeError);
  assert.throws(() => parseDateUTC(""), RangeError);
});
