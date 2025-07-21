# Java로 Oracle 쿼리용 날짜 조건 문자열 생성 (LocalDateTime 사용)

다음은 LocalDateTime을 사용하여 Oracle 쿼리에서 사용할 날짜 조건 문자열을 생성하는 Java 예제입니다.

## 1. 기본 예제

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class OracleDateConditionGenerator {

    public static void main(String[] args) {
        // 현재 시간 사용
        LocalDateTime now = LocalDateTime.now();
        
        // 특정 날짜 사용 시
        // LocalDateTime specificDate = LocalDateTime.of(2023, 5, 15, 14, 30);
        
        // Oracle TO_DATE 형식으로 변환
        String oracleDateCondition = generateOracleDateCondition(now);
        
        System.out.println("Oracle 쿼리 조건: " + oracleDateCondition);
    }

    public static String generateOracleDateCondition(LocalDateTime dateTime) {
        // Oracle의 TO_DATE 형식으로 포맷팅
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formattedDate = dateTime.format(formatter);
        
        return "TO_DATE('" + formattedDate + "', 'YYYY-MM-DD HH24:MI:SS')";
    }
}
```

## 2. 다양한 사용 예제 확장

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class OracleDateQueryBuilder {

    public static void main(String[] args) {
        LocalDateTime startDate = LocalDateTime.of(2023, 5, 1, 0, 0);
        LocalDateTime endDate = LocalDateTime.of(2023, 5, 31, 23, 59, 59);
        
        // 단일 날짜 조건
        System.out.println("단일 날짜 조건: " + 
            generateSingleDateCondition("CREATE_DATE", startDate));
        
        // 기간 조건 (BETWEEN)
        System.out.println("기간 조건: " + 
            generateDateRangeCondition("CREATE_DATE", startDate, endDate));
        
        // 비교 조건 (이후 날짜)
        System.out.println("이후 날짜 조건: " + 
            generateDateComparisonCondition("CREATE_DATE", startDate, ">="));
    }

    // 단일 날짜 조건 생성
    public static String generateSingleDateCondition(String columnName, LocalDateTime dateTime) {
        return columnName + " = " + formatForOracle(dateTime);
    }

    // 날짜 범위 조건 생성 (BETWEEN)
    public static String generateDateRangeCondition(String columnName, 
                                                  LocalDateTime startDate, 
                                                  LocalDateTime endDate) {
        return columnName + " BETWEEN " + formatForOracle(startDate) + 
               " AND " + formatForOracle(endDate);
    }

    // 비교 연산자 사용 조건 생성 (>, <, >=, <= 등)
    public static String generateDateComparisonCondition(String columnName, 
                                                        LocalDateTime dateTime, 
                                                        String operator) {
        return columnName + " " + operator + " " + formatForOracle(dateTime);
    }

    // Oracle TO_DATE 형식으로 포맷팅
    private static String formatForOracle(LocalDateTime dateTime) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formattedDate = dateTime.format(formatter);
        return "TO_DATE('" + formattedDate + "', 'YYYY-MM-DD HH24:MI:SS')";
    }
}
```

## 3. 사용 예시 출력

위 코드를 실행하면 다음과 같은 결과가 출력됩니다:

```
단일 날짜 조건: CREATE_DATE = TO_DATE('2023-05-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
기간 조건: CREATE_DATE BETWEEN TO_DATE('2023-05-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AND TO_DATE('2023-05-31 23:59:59', 'YYYY-MM-DD HH24:MI:SS')
이후 날짜 조건: CREATE_DATE >= TO_DATE('2023-05-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
```

## 4. 활용 팁

1. **다른 날짜 패턴이 필요한 경우**: `DateTimeFormatter`의 패턴을 변경하면 됩니다.
   ```java
   // 날짜만 필요한 경우
   DateTimeFormatter dateOnlyFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
   ```

2. **다른 데이터베이스 호환성**: Oracle 대신 다른 DB를 사용할 경우 `TO_DATE` 대신 해당 DB의 함수로 변경하면 됩니다.

3. **Prepared Statement 사용 시**: 실제 프로덕션 코드에서는 SQL 인젝션 방지를 위해 Prepared Statement를 사용하는 것이 좋습니다. 이 예제는 쿼리 문자열 생성 방법을 보여주기 위한 것입니다.

4. **시간대 고려**: 시간대가 중요한 경우 `ZonedDateTime`을 사용하고 적절히 변환하는 것이 좋습니다.