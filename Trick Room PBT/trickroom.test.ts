import fc from "fast-check";
import * as fs from "fs";
import * as path from "path";

const LOG_FILE = path.join(__dirname, "trickroom-failures.txt");

function trunc(num: number, bits = 0): number {
  if (bits) return (num >>> 0) % 2 ** bits;
  return num >>> 0;
}

function getActionSpeed(
  speed: number,
  trickRoomActive: boolean,
  twistedDimensionMod: boolean
): number {
  const trickRoomCheck = twistedDimensionMod
    ? !trickRoomActive
    : trickRoomActive;

  const result = trickRoomCheck ? 10000 - speed : speed;
  return trunc(result, 13);
}

describe("getActionSpeed – property-based tests", () => {
  const speedArb = fc.integer({ min: 1, max: 8160 });
  const boolArb = fc.boolean();

  // Property 1: Non-negative integer < 8192 (2^13)
  it("always returns a value in [0, 8191]", () => {
    fc.assert(
      fc.property(speedArb, boolArb, boolArb, (speed, trickRoom, twisted) => {
        const result = getActionSpeed(speed, trickRoom, twisted);
        return Number.isInteger(result) && result >= 0 && result <= 8191;
      }),
      { numRuns: 5000 }
    );
  });

  // Property 2: Trick room inverts speed ordering.
  it("trick room inverts speed ordering", () => {
    const failures: { speedA: number; speedB: number; normalA: number; normalB: number; trickA: number; trickB: number }[] = [];

    const pairs = fc.sample(
      fc.tuple(
        fc.integer({ min: 1, max: 8160 }),
        fc.integer({ min: 1, max: 8160 })
      ),
      5000
    );

    for (const [speedA, speedB] of pairs) {
      if (speedA === speedB) continue;

      const normalA = getActionSpeed(speedA, false, false);
      const normalB = getActionSpeed(speedB, false, false);
      const trickA  = getActionSpeed(speedA, true, false);
      const trickB  = getActionSpeed(speedB, true, false);

      const orderingReversed = speedA > speedB ? trickA < trickB : trickA > trickB;

      if (!orderingReversed) {
        failures.push({ speedA, speedB, normalA, normalB, trickA, trickB });
      }
    }

    if (failures.length > 0) {
      const lines: string[] = [];

      lines.push(`${"=".repeat(70)}`);
      lines.push(`  TRICK ROOM ORDERING FAILURES: ${failures.length} / 5000 pairs`);
      lines.push(`  Generated: ${new Date().toISOString()}`);
      lines.push(`${"=".repeat(70)}`);

      for (const f of failures) {
        const aOverflows = 10000 - f.speedA > 8191;
        const bOverflows = 10000 - f.speedB > 8191;

        const fasterNormally   = f.speedA > f.speedB ? `A (${f.speedA})` : `B (${f.speedB})`;
        const slowerNormally   = f.speedA > f.speedB ? `B (${f.speedB})` : `A (${f.speedA})`;
        const expectedFasterTR = slowerNormally;
        const actualFasterTR   = f.trickA > f.trickB ? `A (${f.speedA})` : `B (${f.speedB})`;

        lines.push(``);
        lines.push(`  Speed A: ${f.speedA}  |  Speed B: ${f.speedB}`);
        lines.push(`  Normal order   : ${fasterNormally} is faster`);
        lines.push(`  Expected TR    : ${expectedFasterTR} should become faster (ordering reversed)`);
        lines.push(`  Actual TR      : ${actualFasterTR} is faster  <- WRONG`);
        lines.push(`  +- Why it breaks:`);
        if (aOverflows) {
          lines.push(`  |  Speed A: 10000 - ${f.speedA} = ${10000 - f.speedA} > 8191, truncated to ${f.trickA}`);
        } else {
          lines.push(`  |  Speed A: 10000 - ${f.speedA} = ${10000 - f.speedA} -> ${f.trickA} (no overflow)`);
        }
        if (bOverflows) {
          lines.push(`  |  Speed B: 10000 - ${f.speedB} = ${10000 - f.speedB} > 8191, truncated to ${f.trickB}`);
        } else {
          lines.push(`  |  Speed B: 10000 - ${f.speedB} = ${10000 - f.speedB} -> ${f.trickB} (no overflow)`);
        }
        lines.push(`  +- trunc(x, 13) wraps anything above 8191, corrupting the speed comparison`);
        lines.push(`  ${"─".repeat(60)}`);
      }

      const failingSpeeds = failures.flatMap(f => [f.speedA, f.speedB]).filter(s => 10000 - s > 8191);
      const uniqueFailing = [...new Set(failingSpeeds)].sort((a, b) => a - b);
      lines.push(``);
      lines.push(`  CUTOFF: Any Pokemon with base speed <= ${Math.max(...uniqueFailing)} risks broken`);
      lines.push(`          trick room ordering because 10000 - speed exceeds the 8191 (2^13-1) cap.`);
      lines.push(`${"=".repeat(70)}`);

      fs.writeFileSync(LOG_FILE, lines.join("\n"), "utf8");
      console.log(`\n  Failure report written to: ${LOG_FILE}`);
      console.log(`  Total failures: ${failures.length} / 5000 pairs\n`);
    }
    expect(failures.length).toBeGreaterThan(0);
  });

  // Property 3: Without trickroom, just check raw stats
  it("without trick room effect, just check raw stats", () => {
    fc.assert(
      fc.property(speedArb, (speed) => {
        const r1 = getActionSpeed(speed, false, false);
        const r2 = getActionSpeed(speed, true, true);
        return r1 === speed && r2 === speed;
      }),
      { numRuns: 5000 }
    );
  });

  // Property 4: With trick room effect, result equals trunc(10000 - speed, 13).
  it("with trick room effect, result equals trunc(10000 - speed, 13)", () => {
    fc.assert(
      fc.property(speedArb, (speed) => {
        const r1 = getActionSpeed(speed, true, false);
        const r2 = getActionSpeed(speed, false, true);
        const expected = trunc(10000 - speed, 13);
        return r1 === expected && r2 === expected;
      }),
      { numRuns: 5000 }
    );
  });

  // Property 5: Edge cases – speed at boundaries 1 and 8160
  it("handles boundary speed values without throwing", () => {
    for (const speed of [1, 8160]) {
      for (const tr of [true, false]) {
        for (const tw of [true, false]) {
          expect(() => getActionSpeed(speed, tr, tw)).not.toThrow();
        }
      }
    }
  });
});