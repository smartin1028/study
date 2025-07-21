# Java로 Oracle 쿼리용 날짜 조건 문자열 생성

Oracle 데이터베이스 쿼리에서 사용할 날짜 조건을 문자열로 생성하는 Java 코드를 작성해드리겠습니다.

## 기본 날짜 조건 생성 예제

```java
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

public class OracleDateConditionGenerator {
    
    // 현재 날짜 기준으로 조건 생성
    public static String getTodayCondition(String columnName) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        String today = sdf.format(new Date());
        return columnName + " = TO_DATE('" + today + "', 'YYYY-MM-DD')";
    }
    
    // 특정 날짜 범위 조건 생성
    public static String getDateRangeCondition(String columnName, 
                                             Date startDate, 
                                             Date endDate) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        String start = sdf.format(startDate);
        String end = sdf.format(endDate);
        
        return columnName + " BETWEEN TO_DATE('" + start + "', 'YYYY-MM-DD') " +
               "AND TO_DATE('" + end + "', 'YYYY-MM-DD')";
    }
    
    // 현재 달의 첫날부터 오늘까지 조건 생성
    public static String getCurrentMonthToDateCondition(String columnName) {
        Calendar cal = Calendar.getInstance();
        cal.set(Calendar.DAY_OF_MONTH, 1);
        Date firstDayOfMonth = cal.getTime();
        Date today = new Date();
        
        return getDateRangeCondition(columnName, firstDayOfMonth, today);
    }
    
    // n일 전부터 오늘까지 조건 생성
    public static String getLastNDaysCondition(String columnName, int days) {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_MONTH, -days);
        Date startDate = cal.getTime();
        Date endDate = new Date();
        
        return getDateRangeCondition(columnName, startDate, endDate);
    }
    
    public static void main(String[] args) {
        // 사용 예제
        System.out.println("오늘 날짜 조건: " + 
            getTodayCondition("ORDER_DATE"));
        
        System.out.println("지난 7일 조건: " + 
            getLastNDaysCondition("ORDER_DATE", 7));
        
        System.out.println("이번 달 조건: " + 
            getCurrentMonthToDateCondition("ORDER_DATE"));
    }
}
```

## 고급 기능 추가 버전

```java
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

public class AdvancedOracleDateConditionGenerator {
    
    private static final String ORACLE_DATE_FORMAT = "YYYY-MM-DD";
    private static final String ORACLE_TIMESTAMP_FORMAT = "YYYY-MM-DD HH24:MI:SS";
    
    // 날짜만 있는 조건 (시간 제외)
    public static String createDateCondition(String columnName, Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        return columnName + " = TO_DATE('" + sdf.format(date) + "', '" + ORACLE_DATE_FORMAT + "')";
    }
    
    // 날짜+시간이 있는 조건
    public static String createTimestampCondition(String columnName, Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return columnName + " = TO_TIMESTAMP('" + sdf.format(date) + "', '" + ORACLE_TIMESTAMP_FORMAT + "')";
    }
    
    // 문자열 날짜를 파싱하여 조건 생성
    public static String createConditionFromString(String columnName, 
                                                String dateStr, 
                                                String inputFormat) throws ParseException {
        SimpleDateFormat sdf = new SimpleDateFormat(inputFormat);
        Date date = sdf.parse(dateStr);
        return createDateCondition(columnName, date);
    }
    
    // 동적 쿼리 생성을 위한 날짜 조건 빌더
    public static class DateConditionBuilder {
        private String columnName;
        private Date startDate;
        private Date endDate;
        private boolean includeTime = false;
        
        public DateConditionBuilder(String columnName) {
            this.columnName = columnName;
        }
        
        public DateConditionBuilder setStartDate(Date startDate) {
            this.startDate = startDate;
            return this;
        }
        
        public DateConditionBuilder setEndDate(Date endDate) {
            this.endDate = endDate;
            return this;
        }
        
        public DateConditionBuilder includeTime(boolean include) {
            this.includeTime = include;
            return this;
        }
        
        public String build() {
            if (startDate == null && endDate == null) {
                throw new IllegalStateException("시작일 또는 종료일 중 하나는 설정해야 합니다.");
            }
            
            SimpleDateFormat sdf = includeTime ? 
                new SimpleDateFormat("yyyy-MM-dd HH:mm:ss") : 
                new SimpleDateFormat("yyyy-MM-dd");
            
            String format = includeTime ? ORACLE_TIMESTAMP_FORMAT : ORACLE_DATE_FORMAT;
            String function = includeTime ? "TO_TIMESTAMP" : "TO_DATE";
            
            if (startDate != null && endDate != null) {
                return columnName + " BETWEEN " + function + "('" + sdf.format(startDate) + 
                       "', '" + format + "') AND " + function + "('" + 
                       sdf.format(endDate) + "', '" + format + "')";
            } else if (startDate != null) {
                return columnName + " >= " + function + "('" + sdf.format(startDate) + 
                       "', '" + format + "')";
            } else {
                return columnName + " <= " + function + "('" + sdf.format(endDate) + 
                       "', '" + format + "')";
            }
        }
    }
    
    public static void main(String[] args) throws ParseException {
        // 빌더 패턴 사용 예제
        String condition = new DateConditionBuilder("SALES_DATE")
            .setStartDate(new Date())
            .includeTime(true)
            .build();
        
        System.out.println("빌더로 생성한 조건: " + condition);
        
        // 문자열 파싱 예제
        String strCondition = createConditionFromString(
            "BIRTH_DATE", 
            "1990-05-15", 
            "yyyy-MM-dd");
        
        System.out.println("문자열로 생성한 조건: " + strCondition);
    }
}
```

## 사용 팁

1. **SQL 인젝션 방지**: 실제 프로덕션 코드에서는 PreparedStatement를 사용하는 것이 더 안전합니다.
2. **성능 고려**: 컬럼에 인덱스가 있는 경우 함수로 감싸지 말고 직접 비교하는 것이 좋습니다.
   - `TO_DATE(column) = ...` 대신 `column = TO_DATE(...)` 사용
3. **시간대 처리**: 필요한 경우 시간대를 고려해야 합니다.
4. **날짜 포맷**: Oracle과 Java의 날짜 포맷이 일치해야 합니다.

이 코드들을 필요에 맞게 수정하여 사용하시면 됩니다. 더 구체적인 요구사항이 있으면 알려주세요.