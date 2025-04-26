internal static partial class NativeMethods
{
    [DllImport("__Internal")]
    internal static extern void HealthKitBridge_RequestAuthorization(
	Action<bool, string> completion			
    );

    [DllImport("__Internal")]
    internal static extern void HealhKitBridge_GetSteps(
	double startDate,
	double endDate,
	Action<string, string> completion
    );
}
