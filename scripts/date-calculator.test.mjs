import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { addCalendarDays, calculateDateDifference, formatDateInputValue, getDefaultDateRange, parseDateUTC } from "./date-calculator.mjs";

test("calculates elapsed days, weeks, and weekdays for the article example", () => {
  assert.deepEqual(calculateDateDifference("2026-11-11", "2026-12-19"), {
    days: 38,
    weeks: 5,
    remainingDays: 3,
    weekdays: 27,
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

test("weekday count excludes the start date and includes the end date", () => {
  assert.equal(calculateDateDifference("2026-11-11", "2026-11-14").weekdays, 2);
  assert.equal(calculateDateDifference("2026-11-14", "2026-11-16").weekdays, 1);
  assert.equal(calculateDateDifference("2026-11-13", "2026-11-16").weekdays, 1);
});

test("rejects impossible and malformed calendar dates", () => {
  assert.throws(() => parseDateUTC("2026-02-30"), RangeError);
  assert.throws(() => parseDateUTC("not-a-date"), RangeError);
  assert.throws(() => parseDateUTC(""), RangeError);
});

test("defaults the calculator to the current local date and 38 days later", () => {
  const now = new Date(2026, 10, 14, 12, 0, 0);
  assert.deepEqual(getDefaultDateRange(now), {
    startDate: "2026-11-14",
    endDate: "2026-12-22",
  });
});

test("adds calendar days across leap-day boundaries", () => {
  assert.equal(addCalendarDays("2024-02-28", 2), "2024-03-01");
  assert.throws(() => addCalendarDays("2024-02-28", 1.5), RangeError);
});

test("formats a valid local date for date inputs", () => {
  assert.equal(formatDateInputValue(new Date(2026, 10, 14, 12, 0, 0)), "2026-11-14");
  assert.throws(() => formatDateInputValue(new Date(Number.NaN)), RangeError);
});


test("date calculator copy distinguishes weekdays from business days", () => {
  const article = readFileSync(new URL("../articles/days-between-dates-calculator.html", import.meta.url), "utf8");
  const feed = JSON.parse(readFileSync(new URL("../data/articles.json", import.meta.url), "utf8"));
  const homepage = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const technology = readFileSync(new URL("../section-technology.html", import.meta.url), "utf8");
  const sitemap = readFileSync(new URL("../sitemap.xml", import.meta.url), "utf8");
  const entry = feed.find((item) => item.slug === "days-between-dates-calculator");

  assert.ok(entry, "Date calculator article must remain in the article feed.");
  assert.equal(entry.title, "Days Between Dates Calculator: Count Days, Weeks and Weekdays");
  assert.ok(entry.tags.includes("weekday calculator"));
  assert.ok(!entry.tags.includes("business days calculator"));
  assert.match(article, /does not exclude public holidays/i);
  assert.match(article, /not a business-day calculation/i);
  assert.match(article, /id="start-date" type="date"/);
  assert.match(article, /id="end-date" type="date"/);
  assert.doesNotMatch(article, /id="start-date" type="date" value=/);
  assert.doesNotMatch(article, /id="end-date" type="date" value=/);
  assert.match(article, /Select two dates to calculate the difference/);
  assert.match(article, /Monday-to-Friday weekdays/);
  assert.match(article, /excluding the start date and including the end date/i);
  assert.match(article, /"dateModified":"2026-11-13"/);
  assert.match(article, /Updated November 13, 2026/);
  assert.equal(entry.lastmod, "2026-11-13");
  assert.match(homepage, /Days Between Dates Calculator: Count Days, Weeks and Weekdays/);
  assert.match(technology, /Days Between Dates Calculator: Count Days, Weeks and Weekdays/);
  assert.match(sitemap, /<loc>https:\/\/publication\.today\/articles\/days-between-dates-calculator\.html<\/loc>\s*<lastmod>2026-11-13<\/lastmod>/);
});
