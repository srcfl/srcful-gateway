import { mount, config } from "@vue/test-utils";
import { beforeAll, describe, expect, test } from "vitest";
import Preview from "./Preview.vue";
import type { Slot } from "@/types/evcc";

config.global.mocks["$i18n"] = { locale: "de-DE" };
config.global.mocks["$t"] = (a: any) => a;

describe("basics", () => {
  const DATE_START = new Date("2023-01-11T11:00:00+01:00");
  const DATE_TARGET = new Date("2023-01-11T13:00:00+01:00");
  const TARIFF_FIXED = [
    {
      start: new Date("2023-01-11T11:00:00+01:00"),
      end: new Date("2023-01-22T00:00:00+01:00"),
      value: 0.4,
    },
  ];
  const PLAN = [
    {
      start: new Date("2023-01-11T12:00:00+01:00"),
      end: new Date("2023-01-11T13:00:00+01:00"),
      value: 0.2,
    },
  ];

  const wrapper = mount(Preview, {
    props: {
      plan: PLAN,
      targetTime: DATE_TARGET,
      rates: TARIFF_FIXED,
    },
  });
  wrapper.setData({ startTime: DATE_START });

  let result: Slot[];

  beforeAll(() => {
    result = wrapper.vm.slots;
  });

  test("should return 39 slots", () => {
    expect(result.length).eq(39);
  });

  test("slots should be an hour apart", () => {
    expect(result[0].startHour).eq(11);
    expect(result[0].endHour).eq(12);
    expect(result[0].day).eq("Mi");

    expect(result[1].startHour).eq(12);
    expect(result[1].endHour).eq(13);
    expect(result[1].day).eq("Mi");

    expect(result[11].startHour).eq(22);
    expect(result[11].endHour).eq(23);
    expect(result[11].day).eq("Mi");

    expect(result[24].startHour).eq(11);
    expect(result[24].endHour).eq(12);
    expect(result[24].day).eq("Do");
  });

  test("slots after target should be toLate", () => {
    expect(result[0].toLate).eq(false);
    expect(result[1].toLate).eq(false);
    expect(result[2].toLate).eq(true);
    expect(result[3].toLate).eq(true);
  });

  test("slots are marked if charging is happening in them", () => {
    expect(result[0].charging).eq(false);
    expect(result[1].charging).eq(true);
    expect(result[2].charging).eq(false);
    expect(result[3].charging).eq(false);
  });

  test("all slots have the same fixed value", () => {
    result.forEach((slot) => expect(slot.value).eq(0.4));
  });
});

describe("zoned tariffs", () => {
  const DATE_START = new Date("2023-01-11T11:00:00+01:00");
  const DATE_TARGET = new Date("2023-01-11T16:00:00+01:00");
  const TARIFF_ZONED = [
    {
      start: new Date("2023-01-11T11:00:00+01:00"),
      end: new Date("2023-01-11T12:00:00+01:00"),
      value: 0.2,
    },
    {
      start: new Date("2023-01-11T12:00:00+01:00"),
      end: new Date("2023-01-22T00:00:00+01:00"),
      value: 0.4,
    },
  ];
  const PLAN = [
    {
      start: new Date("2023-01-11T11:30:00+01:00"),
      end: new Date("2023-01-11T13:00:00+01:00"),
      value: 0.3,
    },
    {
      start: new Date("2023-01-11T14:30:00+01:00"),
      end: new Date("2023-01-11T16:00:00+01:00"),
      value: 0.2,
    },
  ];

  let result: Slot[];

  const wrapper = mount(Preview, {
    props: {
      plan: PLAN,
      targetTime: DATE_TARGET,
      rates: TARIFF_ZONED,
    },
  });
  wrapper.setData({ startTime: DATE_START });

  beforeAll(() => {
    result = wrapper.vm.slots;
  });

  test("handle multiple charging slots", () => {
    expect(result[0].charging).eq(true);
    expect(result[1].charging).eq(true);
    expect(result[2].charging).eq(false);
    expect(result[3].charging).eq(true);
    expect(result[4].charging).eq(true);
    expect(result[5].charging).eq(false);
  });

  test("first slot is cheap, others are expensive", () => {
    const [first, ...others] = result;
    expect(first.value).eq(0.2);
    others.forEach((slot) => expect(slot.value).eq(0.4));
  });
});
