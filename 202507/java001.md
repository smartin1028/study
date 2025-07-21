# Java에서 30일을 5일 단위로 나누어 조회하는 방법

30일 기간을 5일씩 나누어 조회하는 Java 코드를 작성해드리겠습니다. 이 방법은 대용량 데이터를 조회할 때 성능을 향상시키거나 API 호출 제한이 있을 때 유용합니다.

## 1. 날짜 범위 분할 클래스

먼저 날짜 범위를 저장할 간단한 클래스를 생성합니다.

```java
import java.time.LocalDate;

public class DateRange {
    private LocalDate fromDate;
    private LocalDate toDate;

    public DateRange(LocalDate fromDate, LocalDate toDate) {
        this.fromDate = fromDate;
        this.toDate = toDate;
    }

    public LocalDate getFromDate() {
        return fromDate;
    }

    public LocalDate getToDate() {
        return toDate;
    }

    @Override
    public String toString() {
        return "From: " + fromDate + " To: " + toDate;
    }
}
```

## 2. 날짜 분할 유틸리티 클래스

30일을 5일 단위로 분할하는 유틸리티 메서드를 작성합니다.

```java
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

public class DateSplitter {

    public static List<DateRange> splitDateRange(LocalDate startDate, LocalDate endDate, int days) {
        List<DateRange> dateRanges = new ArrayList<>();
        
        long totalDays = ChronoUnit.DAYS.between(startDate, endDate) + 1;
        long chunks = (totalDays + days - 1) / days; // 올림 계산
        
        for (int i = 0; i < chunks; i++) {
            LocalDate chunkStart = startDate.plusDays(i * days);
            LocalDate chunkEnd = chunkStart.plusDays(days - 1);
            
            // 마지막 청크가 endDate를 넘지 않도록 조정
            if (chunkEnd.isAfter(endDate)) {
                chunkEnd = endDate;
            }
            
            dateRanges.add(new DateRange(chunkStart, chunkEnd));
        }
        
        return dateRanges;
    }
}
```

## 3. 사용 예제

```java
import java.time.LocalDate;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        LocalDate startDate = LocalDate.now().minusDays(29); // 오늘 포함 30일
        LocalDate endDate = LocalDate.now();
        
        List<DateRange> dateRanges = DateSplitter.splitDateRange(startDate, endDate, 5);
        
        // 분할된 날짜 범위 출력
        for (DateRange range : dateRanges) {
            System.out.println(range);
        }
        
        // 실제 조회 로직 (예시)
        for (DateRange range : dateRanges) {
            List<Data> dataList = fetchData(range.getFromDate(), range.getToDate());
            // 데이터 처리...
        }
    }
    
    // 가상의 데이터 조회 메서드 (실제 구현에 따라 변경 필요)
    private static List<Data> fetchData(LocalDate fromDate, LocalDate toDate) {
        System.out.println("조회 중: " + fromDate + " ~ " + toDate);
        // 실제 데이터베이스 조회 또는 API 호출 로직
        return new ArrayList<>();
    }
}

// 가상의 데이터 클래스
class Data {
    // 데이터 필드
}
```

## 4. 실행 결과 예시

```
From: 2023-11-02 To: 2023-11-06
From: 2023-11-07 To: 2023-11-11
From: 2023-11-12 To: 2023-11-16
From: 2023-11-17 To: 2023-11-21
From: 2023-11-22 To: 2023-11-26
From: 2023-11-27 To: 2023-12-01
```

## 5. 실제 적용 시 고려사항

1. **데이터베이스 조회**: 각 날짜 범위에 대해 별도의 쿼리를 실행
   ```java
   for (DateRange range : dateRanges) {
       String query = "SELECT * FROM table WHERE date BETWEEN ? AND ?";
       PreparedStatement stmt = connection.prepareStatement(query);
       stmt.setDate(1, Date.valueOf(range.getFromDate()));
       stmt.setDate(2, Date.valueOf(range.getToDate()));
       ResultSet rs = stmt.executeQuery();
       // 결과 처리
   }
   ```

2. **API 호출**: 외부 API에 날짜 범위를 전달하여 호출
   ```java
   for (DateRange range : dateRanges) {
       String url = "https://api.example.com/data?from=" + range.getFromDate() + 
                    "&to=" + range.getToDate();
       // HTTP 클라이언트로 호출
   }
   ```

3. **병렬 처리**: 큰 데이터를 처리할 경우 `parallelStream()` 사용 고려
   ```java
   dateRanges.parallelStream().forEach(range -> {
       fetchData(range.getFromDate(), range.getToDate());
   });
   ```

이 코드는 Java 8 이상의 `java.time` 패키지를 사용하며, 30일 기간을 5일 단위로 정확히 분할하여 각각의 시작일과 종료일을 제공합니다.