# Java에서 LocalDateTime과 문자열 간 변환 방법

Java 8 이상에서 `LocalDateTime`과 문자열 간 변환은 `DateTimeFormatter`를 사용하여 수행할 수 있습니다. 아래에 상세한 방법을 설명드리겠습니다.

## 1. LocalDateTime을 문자열로 변환

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class LocalDateTimeToString {
    public static void main(String[] args) {
        // 현재 LocalDateTime 객체 생성
        LocalDateTime now = LocalDateTime.now();
        
        // 기본 포맷으로 출력 (ISO-8601)
        String defaultFormat = now.toString();
        System.out.println("기본 포맷: " + defaultFormat);
        
        // 커스텀 포맷 지정
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formattedDateTime = now.format(formatter);
        System.out.println("커스텀 포맷: " + formattedDateTime);
        
        // 다른 예시 포맷
        DateTimeFormatter anotherFormatter = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 E요일 a hh시 mm분 ss초");
        String anotherFormatted = now.format(anotherFormatter);
        System.out.println("다른 포맷: " + anotherFormatted);
    }
}
```

### 주요 포맷 패턴 설명:
- `yyyy`: 4자리 연도
- `MM`: 2자리 월 (01~12)
- `dd`: 2자리 일 (01~31)
- `HH`: 24시간 형식 시간 (00~23)
- `hh`: 12시간 형식 시간 (01~12)
- `mm`: 분 (00~59)
- `ss`: 초 (00~59)
- `a`: 오전/오후
- `E`: 요일 (월, 화, 수 등)

## 2. 문자열을 LocalDateTime으로 변환

```java
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class StringToLocalDateTime {
    public static void main(String[] args) {
        // 문자열 예시
        String dateTimeStr1 = "2023-05-15T14:30:45"; // ISO-8601 형식
        String dateTimeStr2 = "2023-05-15 14:30:45"; // 커스텀 형식
        String dateTimeStr3 = "2023년 05월 15일 14시 30분 45초"; // 다른 형식
        
        // ISO-8601 형식 파싱
        LocalDateTime dateTime1 = LocalDateTime.parse(dateTimeStr1);
        System.out.println("ISO-8601 파싱: " + dateTime1);
        
        // 커스텀 형식 파싱
        DateTimeFormatter formatter1 = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        LocalDateTime dateTime2 = LocalDateTime.parse(dateTimeStr2, formatter1);
        System.out.println("커스텀 포맷 파싱: " + dateTime2);
        
        // 다른 형식 파싱
        DateTimeFormatter formatter2 = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 HH시 mm분 ss초");
        LocalDateTime dateTime3 = LocalDateTime.parse(dateTimeStr3, formatter2);
        System.out.println("다른 포맷 파싱: " + dateTime3);
    }
}
```

## 주의사항

1. **예외 처리**: `DateTimeParseException`이 발생할 수 있으므로 적절한 예외 처리가 필요합니다.
   ```java
   try {
       LocalDateTime dateTime = LocalDateTime.parse(dateString, formatter);
   } catch (DateTimeParseException e) {
       System.err.println("날짜 형식이 잘못되었습니다: " + e.getMessage());
   }
   ```

2. **시간대 처리**: `LocalDateTime`은 시간대 정보를 포함하지 않습니다. 시간대가 필요한 경우 `ZonedDateTime`을 사용하세요.

3. **포맷 일치**: 문자열과 포맷 패턴이 정확히 일치해야 합니다. 불일치 시 예외가 발생합니다.

4. **불변성**: `LocalDateTime` 객체는 불변(immutable)이므로 모든 변환 작업은 새로운 객체를 생성합니다.

이러한 방법들을 활용하면 Java에서 `LocalDateTime`과 문자열 간의 변환을 자유롭게 수행할 수 있습니다.