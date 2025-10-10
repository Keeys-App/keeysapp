import { describe, it, expect } from "vitest";
import { parseI18nFormat, detectFormat } from "./importFormats";

describe("parseI18nFormat", () => {
  it("should parse flat key-value pairs", () => {
    const content = JSON.stringify({
      "WELCOME": "Welcome!",
      "HELLO": "Hello",
      "GOODBYE": "Goodbye",
    });

    const result = parseI18nFormat(content);

    expect(result.success).toBe(true);
    expect(result.translations).toHaveLength(3);
    expect(result.translations).toEqual([
      { key: "WELCOME", value: "Welcome!" },
      { key: "HELLO", value: "Hello" },
      { key: "GOODBYE", value: "Goodbye" },
    ]);
  });

  it("should parse nested objects into dot-notation keys", () => {
    const content = JSON.stringify({
      "AUTH": {
        "LOGIN": "Login",
        "LOGOUT": "Logout",
        "REGISTER": "Register",
      },
    });

    const result = parseI18nFormat(content);

    expect(result.success).toBe(true);
    expect(result.translations).toHaveLength(3);
    expect(result.translations).toEqual([
      { key: "AUTH.LOGIN", value: "Login" },
      { key: "AUTH.LOGOUT", value: "Logout" },
      { key: "AUTH.REGISTER", value: "Register" },
    ]);
  });

  it("should parse deeply nested objects", () => {
    const content = JSON.stringify({
      "AUTH": {
        "WEBAUTHN": {
          "WEBAUTHN_NOT_SUPPORTED": "WebAuthn is not supported in this browser",
          "WEBAUTHN_FAILED": "WebAuthn authentication failed",
        },
      },
    });

    const result = parseI18nFormat(content);

    expect(result.success).toBe(true);
    expect(result.translations).toHaveLength(2);
    expect(result.translations).toEqual([
      { key: "AUTH.WEBAUTHN.WEBAUTHN_NOT_SUPPORTED", value: "WebAuthn is not supported in this browser" },
      { key: "AUTH.WEBAUTHN.WEBAUTHN_FAILED", value: "WebAuthn authentication failed" },
    ]);
  });

  it("should parse mixed flat and nested keys", () => {
    const content = JSON.stringify({
      "AUTH.WEBAUTHN.WEBAUTHN_NOT_SUPPORTED": "WebAuthn is not supported in this browser",
      "AUTH.WELCOME_BACK": "Welcome back!",
      "AUTH.WHATS_YOUR_FULL_NAME": "What is your name?",
      "AUTH": {
        "ADD_ANOTHER_EMAIL": "Add another email",
        "CHECK_VERIFICATION_EMAIL": "Check the verification email sent to this address.",
        "EMAIL_FOR_LOGIN_AND_NOTIFICATIONS": "This email is for log in and account notifications.",
        "EMAIL_PLACEHOLDER": "Enter your email",
        "RESEND_VERIFICATION_MAIL": "Resend verification mail",
      },
      "AUTOMATIONS.LIMITS_BANNER.LINK": "Switch to a higher plan",
    });

    const result = parseI18nFormat(content);

    expect(result.success).toBe(true);
    expect(result.translations).toHaveLength(9);
    
    // Check that flat keys with dots are preserved
    expect(result.translations).toContainEqual({
      key: "AUTH.WEBAUTHN.WEBAUTHN_NOT_SUPPORTED",
      value: "WebAuthn is not supported in this browser",
    });
    expect(result.translations).toContainEqual({
      key: "AUTH.WELCOME_BACK",
      value: "Welcome back!",
    });
    
    // Check that nested keys are flattened
    expect(result.translations).toContainEqual({
      key: "AUTH.ADD_ANOTHER_EMAIL",
      value: "Add another email",
    });
    expect(result.translations).toContainEqual({
      key: "AUTH.EMAIL_PLACEHOLDER",
      value: "Enter your email",
    });
  });

  it("should skip null and undefined values", () => {
    const content = JSON.stringify({
      "VALID": "Valid value",
      "NULL_VALUE": null,
      "UNDEFINED_VALUE": undefined,
      "ANOTHER_VALID": "Another valid value",
    });

    const result = parseI18nFormat(content);

    expect(result.success).toBe(true);
    expect(result.translations).toHaveLength(2);
    expect(result.translations).toEqual([
      { key: "VALID", value: "Valid value" },
      { key: "ANOTHER_VALID", value: "Another valid value" },
    ]);
  });

  it("should handle empty objects", () => {
    const content = JSON.stringify({});

    const result = parseI18nFormat(content);

    expect(result.success).toBe(false);
    expect(result.error).toBe("No translations found in the file");
  });

  it("should handle invalid JSON", () => {
    const content = "{ invalid json }";

    const result = parseI18nFormat(content);

    expect(result.success).toBe(false);
    expect(result.error).toContain("Failed to parse JSON");
  });

  it("should handle arrays", () => {
    const content = JSON.stringify(["item1", "item2"]);

    const result = parseI18nFormat(content);

    expect(result.success).toBe(false);
    expect(result.error).toBe("Invalid format: Expected a JSON object with key-value pairs");
  });

  it("should handle nested objects with mixed valid and invalid values", () => {
    const content = JSON.stringify({
      "AUTH": {
        "LOGIN": "Login",
        "INVALID": 123,
        "LOGOUT": "Logout",
      },
    });

    const result = parseI18nFormat(content);

    // Should still succeed and skip invalid values
    expect(result.success).toBe(true);
    expect(result.translations).toHaveLength(2);
    expect(result.translations).toEqual([
      { key: "AUTH.LOGIN", value: "Login" },
      { key: "AUTH.LOGOUT", value: "Logout" },
    ]);
  });
});

describe("detectFormat", () => {
  it("should detect i18n format for flat objects", () => {
    const content = JSON.stringify({
      "WELCOME": "Welcome!",
      "HELLO": "Hello",
    });

    const format = detectFormat(content);

    expect(format).toBe("i18n");
  });

  it("should detect i18n format for nested objects", () => {
    const content = JSON.stringify({
      "AUTH": {
        "LOGIN": "Login",
        "LOGOUT": "Logout",
      },
    });

    const format = detectFormat(content);

    expect(format).toBe("i18n");
  });

  it("should detect i18n format for deeply nested objects", () => {
    const content = JSON.stringify({
      "AUTH": {
        "WEBAUTHN": {
          "NOT_SUPPORTED": "Not supported",
        },
      },
    });

    const format = detectFormat(content);

    expect(format).toBe("i18n");
  });

  it("should detect i18n format for mixed flat and nested keys", () => {
    const content = JSON.stringify({
      "FLAT.KEY": "Flat value",
      "AUTH": {
        "LOGIN": "Login",
      },
    });

    const format = detectFormat(content);

    expect(format).toBe("i18n");
  });

  it("should not detect format for invalid JSON", () => {
    const content = "{ invalid json }";

    const format = detectFormat(content);

    expect(format).toBeNull();
  });

  it("should not detect format for arrays", () => {
    const content = JSON.stringify(["item1", "item2"]);

    const format = detectFormat(content);

    expect(format).toBeNull();
  });

  it("should not detect format for objects with invalid values", () => {
    const content = JSON.stringify({
      "VALID": "Valid",
      "INVALID": 123,
    });

    const format = detectFormat(content);

    expect(format).toBeNull();
  });

  it("should not detect format for nested objects with invalid values", () => {
    const content = JSON.stringify({
      "AUTH": {
        "LOGIN": "Login",
        "INVALID": ["array"],
      },
    });

    const format = detectFormat(content);

    expect(format).toBeNull();
  });
});

