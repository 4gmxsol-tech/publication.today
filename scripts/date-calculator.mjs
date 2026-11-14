export function parseDateUTC(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value ?? "");
  if (!match) throw new RangeError("Enter a valid date.");

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (year < 1 || month < 1 || month > 12 || day < 1 || day > 31) {
    throw new RangeError("Enter a valid date.");
  }

  const date = new Date(0);
  date.setUTCHours(0, 0, 0, 0);
  date.setUTCFullYear(year, month - 1, day);
  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    throw new RangeError("Enter a valid date.");
  }
  return date.getTime();
}

export function formatDateInputValue(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    throw new RangeError("Enter a valid date.");
  }

  const year = String(date.getFullYear()).padStart(4, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return year + "-" + month + "-" + day;
}

export function addCalendarDays(value, days) {
  if (!Number.isInteger(days)) {
    throw new RangeError("Enter a whole number of days.");
  }

  const date = new Date(parseDateUTC(value));
  date.setUTCDate(date.getUTCDate() + days);
  const year = String(date.getUTCFullYear()).padStart(4, "0");
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  return year + "-" + month + "-" + day;
}

export function getDefaultDateRange(now = new Date()) {
  const startDate = formatDateInputValue(now);
  return {
    startDate,
    endDate: addCalendarDays(startDate, 38),
  };
}

function countWeekdays(startTime, dayCount) {
  const fullWeeks = Math.floor(dayCount / 7);
  const remainingDays = dayCount % 7;
  let weekdays = fullWeeks * 5;
  const startDay = (new Date(startTime).getUTCDay() + 1) % 7;

  for (let offset = 0; offset < remainingDays; offset += 1) {
    const weekday = (startDay + offset) % 7;
    if (weekday !== 0 && weekday !== 6) weekdays += 1;
  }
  return weekdays;
}

export function calculateDateDifference(startValue, endValue) {
  const startTime = parseDateUTC(startValue);
  const endTime = parseDateUTC(endValue);
  const earlier = Math.min(startTime, endTime);
  const later = Math.max(startTime, endTime);
  const days = (later - earlier) / 86_400_000;
  const weeks = Math.floor(days / 7);

  return {
    days,
    weeks,
    remainingDays: days % 7,
    weekdays: countWeekdays(earlier, days),
  };
}

if (typeof document !== "undefined") {
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  const startInput = document.getElementById("start-date");
  const endInput = document.getElementById("end-date");
  const calculateButton = document.getElementById("date-calculate");
  const result = document.getElementById("date-result");

  const defaultRange = getDefaultDateRange();
  if (startInput && !startInput.value) startInput.value = defaultRange.startDate;
  if (endInput && !endInput.value) endInput.value = defaultRange.endDate;

  function updateDateResult() {
    if (!startInput || !endInput || !result) return;
    if (!startInput.value || !endInput.value) {
      result.textContent = "Please choose both dates.";
      return;
    }

    try {
      const { days, weeks, remainingDays, weekdays } = calculateDateDifference(
        startInput.value,
        endInput.value,
      );
      const dayLabel = days === 1 ? "day" : "days";
      const weekLabel = weeks === 1 ? "week" : "weeks";
      const remainderLabel = remainingDays === 1 ? "day" : "days";
      const detail = document.createElement("span");
      detail.className = "date-sub";
      detail.textContent =
        weeks + " " + weekLabel + " and " + remainingDays + " " +
        remainderLabel + " · " + weekdays + " weekdays (Monday–Friday)";
      result.replaceChildren(
        document.createTextNode(days + " " + dayLabel + " apart."),
        document.createElement("br"),
        detail,
      );
    } catch {
      result.textContent = "Please choose two valid dates.";
    }
  }

  if (calculateButton) calculateButton.addEventListener("click", updateDateResult);
  if (startInput) startInput.addEventListener("change", updateDateResult);
  if (endInput) endInput.addEventListener("change", updateDateResult);
  updateDateResult();
}
