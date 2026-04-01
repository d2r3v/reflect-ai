import { Colors } from "../src/constants/colors";

describe("Colors", () => {
  it("should have all required colors defined", () => {
    expect(Colors.primary).toBeDefined();
    expect(Colors.secondary).toBeDefined();
    expect(Colors.danger).toBeDefined();
    expect(Colors.background).toBeDefined();
    expect(Colors.surface).toBeDefined();
    expect(Colors.text).toBeDefined();
  });

  it("should have valid color hex values", () => {
    const hexRegex = /^#[0-9A-F]{6}$/i;
    Object.values(Colors).forEach((color) => {
      expect(hexRegex.test(color)).toBe(true);
    });
  });
});
