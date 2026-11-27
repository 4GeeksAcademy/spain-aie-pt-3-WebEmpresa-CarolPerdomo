import * as authClient from "../lib/auth-client";

describe("Backoffice auth client", () => {
  const storage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  };
  const dispatchEvent = jest.fn();

  beforeEach(() => {
    jest.resetAllMocks();
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: { localStorage: storage, dispatchEvent },
    });
    jest.spyOn(globalThis, "fetch").mockResolvedValue({ status: 200 } as Response);
  });

  afterEach(() => {
    jest.restoreAllMocks();
    Reflect.deleteProperty(globalThis, "window");
  });

  it("reads, saves, and clears a token", () => {
    storage.getItem.mockReturnValue("session-token");

    expect(authClient.getAuthToken()).toBe("session-token");
    authClient.saveAuthToken("new-token");
    authClient.clearAuthToken();

    expect(storage.getItem).toHaveBeenCalledWith("nexova_access_token");
    expect(storage.setItem).toHaveBeenCalledWith("nexova_access_token", "new-token");
    expect(storage.removeItem).toHaveBeenCalledWith("nexova_access_token");
  });

  it.each([
    ["read", () => authClient.getAuthToken(), "getItem"],
    ["save", () => authClient.saveAuthToken("token"), "setItem"],
    ["clear", () => authClient.clearAuthToken(), "removeItem"],
  ])("surfaces storage errors when it cannot %s a token", (_action, operation, method) => {
    storage[method as keyof typeof storage].mockImplementation(() => {
      throw new Error("storage unavailable");
    });

    expect(operation).toThrow("storage unavailable");
  });

  it("sends the bearer token, preserves caller headers, and disables caching", async () => {
    storage.getItem.mockReturnValue("session-token");
    const headers = new Headers({ "X-Request-Id": "request-1" });

    await authClient.apiFetch("/api/auth/me", { headers });

    const [, init] = jest.mocked(fetch).mock.calls[0]!;
    expect(new Headers(init?.headers).get("Authorization")).toBe("Bearer session-token");
    expect(new Headers(init?.headers).get("X-Request-Id")).toBe("request-1");
    expect(init?.cache).toBe("no-store");
  });

  it("omits authorization without a token", async () => {
    storage.getItem.mockReturnValue(null);

    await authClient.apiFetch("/api/auth/me");

    expect(new Headers(jest.mocked(fetch).mock.calls[0]![1]?.headers).has("Authorization")).toBe(false);
  });

  it("clears the session and broadcasts unauthorized after a 401", async () => {
    storage.getItem.mockReturnValue("expired-token");
    jest.mocked(fetch).mockResolvedValue({ status: 401 } as Response);

    await authClient.apiFetch("/api/auth/me");

    expect(storage.removeItem).toHaveBeenCalledWith("nexova_access_token");
    expect(dispatchEvent.mock.calls[0]![0]).toMatchObject({ type: "nexova:unauthorized" });
  });

  it("keeps the session on other HTTP statuses and propagates network errors", async () => {
    storage.getItem.mockReturnValue("valid-token");
    jest.mocked(fetch).mockResolvedValueOnce({ status: 400 } as Response);

    await authClient.apiFetch("/api/auth/me");
    expect(storage.removeItem).not.toHaveBeenCalled();

    jest.mocked(fetch).mockRejectedValueOnce(new TypeError("network unavailable"));
    await expect(authClient.apiFetch("/api/auth/me")).rejects.toThrow("network unavailable");
  });
});
