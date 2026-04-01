import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { AppStackParamList } from "./types";
import HomeScreen from "../screens/HomeScreen";
import ChatScreen from "../screens/ChatScreen";
import MoodCheckinScreen from "../screens/MoodCheckinScreen";
import MemoryInspectorScreen from "../screens/MemoryInspectorScreen";
import CrisisSupportScreen from "../screens/CrisisSupportScreen";

const Stack = createNativeStackNavigator<AppStackParamList>();
const Tab = createBottomTabNavigator();

/**
 * AppNavigator
 * Handles in-app navigation for authenticated users.
 * Uses a tab-based layout with nested stacks for feature organization.
 */
export function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          title: "Home",
          tabBarLabel: "Home",
        }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatScreen}
        options={{
          title: "Chat",
          tabBarLabel: "Chat",
        }}
      />
      <Tab.Screen
        name="MoodCheckin"
        component={MoodCheckinScreen}
        options={{
          title: "Mood",
          tabBarLabel: "Mood",
        }}
      />
      <Tab.Screen
        name="MemoryInspector"
        component={MemoryInspectorScreen}
        options={{
          title: "Memory",
          tabBarLabel: "Memory",
        }}
      />
      <Tab.Screen
        name="CrisisSupport"
        component={CrisisSupportScreen}
        options={{
          title: "Crisis Support",
          tabBarLabel: "Crisis",
        }}
      />
    </Tab.Navigator>
  );
}
