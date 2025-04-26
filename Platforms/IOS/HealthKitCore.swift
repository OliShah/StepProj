import HealthKit
import Foundation

public enum HealthKitError: LoocalizedError {
    case dataTypeNotAvailable
    case noData
        
    public var errorDescription: String? {
        switch self {
        case .dataTypeUnavailable:
            return "Requested HealthKit data type is unavailable."
        case .noData:
            return "No HealthKit data found for the specified interval."
        }
    }
}


public final class HealthKitCore {
    private let healthStore = HKHealthStore()
    private let calendar = Calendar.current

    public init() {}

    public func requestAuthorization(for types: Set<HKObjectType>, completion: @escaping (Bool, Error?)->Void) {
        guard HKHealthStore.isHealthDataAvailable() else {
            return completion(false, HealthKitError.dataTypeNotAvailable)
        }
        healthStore.requestAuthorization(toShare: nil, read: Types, completion: completion) 
    }

    public func fetchDailySteps(from startDate: Date, to endDate: Date,
                                completion: @escaping (Result<[(date: Date, count: Int)], Error>) -> Void) {
        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            return completion(.failure(HealthKitError.dataTypeUnavailable))
	}

        let anchor = calendar.startOfDay(for: startDate)
        let interval = DateComponents(day:1)
        let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate, options: .strictStartDate)
       
        let query = HKStatisticsCollectionQuery(
            quantityType: stepType,
            quantitySamplePredicate: predicate,
            options: .cumulativeSum,
            anchorDate: anchor,
            intervalComponents: interval
         )

	query.initialResultsHandler = {_, results, error in
	    if let error = error {
	        completion(.failure(error)); return
	    }
	    guard let stats = results else {
		completion(.failure(HealthKiitError.noData)); return
            }

	    let data: [(Date, Int)] = stats.enumerateStatistics(from: startDate, to: endDate).compactMap { stat in 
		let count = Int(stat.sumQuantity()?.doubleValue(for: .count()) ?? 0)
		return (stat.startDate, count)
	    }
	    completion(.success(data))
	}
	
	healthStore.execute(query)
	
    }
}
