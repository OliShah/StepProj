FILE STRUCTURE:

YourMauiApp/
├── Platforms/
│   └── iOS/
│       ├── HealthKitCore.swift 
│       ├── HealthKitBridge.swift 
│       ├── NativeMethods.cs 
│       ├── Info.plist 
│       └── Entitlements.plist 
│
├── Services/
│   ├── Interfaces/
│   │   └── IHealthKitService.cs           # Service interface
│   │
│   ├── HealthKitService.cs                # Shared service partial class
│   └── HealthKitService.ios.cs            # iOS implementation
│
├── Models/
│   └── StepData.cs                        # Data model
│
├── ViewModels/
│   └── StepsViewModel.cs                  # ViewModel
│
├── Views/
│   ├── StepsPage.xaml                     # UI markup
│   └── StepsPage.xaml.cs                  # Code-behind
│
├── App.xaml
├── App.xaml.cs
└── MauiProgram.cs                         # Dependency registration

NativeMethods:
-A Concrete Service-Class which exposes access to IOS functionality to the 
 application
-Declares two extern methods¹ (<HealthKitBridge_RequestAuthorizatoin> and 
 <HealthKitBridge_GetSteps>) which exist in the app's native binary 
 via <DllImport("__internal">)
-Results retrieved via Action<...> delegates. So when the native code finishes 
 (success or error), it calls back in to C# with appropriate data

¹extern methods are declarations in C# which instructs the compiler the 
 implementation lives outside the C# managed assembly 


HealthKitBridge:
-A Concrete Service-Class playing the role of a Facade or Adapter.
-Recieves method calls from <NativeMethods> and translates those calls 
 (and Obj-C types) into Swift, handles threading/serialisation and delegates
 to HealthKitCore
-<NativeMethods> is the only external entry point


HealthKitCore:
-A Gateway-Class exposing access to HealthKitApi
-The only module that talks directly to HealthKit API. Requesting 
 authorisation and running queries.
-<HealthKitBridge> is the only external entry point 

Entitlements:
-Grants the application the permission to access to specified 
 HealthKit records
-Accessed only by Apple at buildtime

info.plist:
-Supplies the user-facing text that iOS displays in the permission
 alert 
-Accessed only by Apple at runtime
