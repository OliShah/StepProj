import Foundation
import HealthKit

@objc public class HealthKitBridge: NSObject {
    private let core = HealthKitCore()
    @objc public static let shared = HealthKitBridge()

    @objc public func requestAuthorization(completion: @escaping (Bool, String?) -> Void) {
	guard let stepType = HKObjectType.quantityType(forIdentifier: .stepCount) else {
	    return completion(false, "Step count data type not available")
	 }
	 core.requestAuthorization(for: [stepType]) { success, error in
	     DispatchQueue.main.async {
		 completion(success, error?.localizedDescription)
	     }
	 }
     }

     @objc public func getSteps(from startDate: Date, to endDate: Date,
			         completion: @escaping (String?, String?) -> Void) {
         core.fetchDailySteps(from: startDate, to: endDate) { result in
	     DispatchQueue.main.async {
	        switch result {
	        case .success(let data):
		    let jsonArray = data.map { ["date": ISO8601DateFormatter().string(from: $0.0), "count": $0.1] }
		    if let json = try? JSONSerialization.data(with JSONObject: jsonArray),
		       let str = String(data: json, encoding: .utf8) {
		        completion(str, nil)
		    } else {
		        completion(nil, "Failed to encode data")
		    }
	        case .failure(let error):
		     completion(nil, error.localizedDescription)
	        }
	    }
        }
    }
}
