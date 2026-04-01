import React from "react";
import renderer from "react-test-renderer";
import { NavigationContainer } from "@react-navigation/native";
import { RootNavigator } from "../src/navigation/RootNavigator";

describe("Navigation", () => {
  it("RootNavigator renders without crashing", () => {
    const tree = renderer
      .create(
        <NavigationContainer>
          <RootNavigator />
        </NavigationContainer>
      )
      .toJSON();
    expect(tree).toBeTruthy();
  });
});
