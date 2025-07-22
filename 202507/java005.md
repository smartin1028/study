# Java Tablesaw 라이브러리를 이용한 DB 결과 연동 및 CSV 파일 생성 가이드

Tablesaw는 Java용 데이터 프레임 라이브러리로, 데이터 분석과 처리를 쉽게 할 수 있게 해줍니다. 데이터베이스에서 데이터를 가져와 Tablesaw로 처리한 후 CSV 파일로 저장하는 전체 과정을 설명드리겠습니다.

## 1. 환경 설정

### 의존성 추가 (Maven)

```xml
<dependencies>
    <!-- Tablesaw core -->
    <dependency>
        <groupId>tech.tablesaw</groupId>
        <artifactId>tablesaw-core</artifactId>
        <version>0.43.1</version>
    </dependency>
    
    <!-- JDBC 연동을 위한 모듈 -->
    <dependency>
        <groupId>tech.tablesaw</groupId>
        <artifactId>tablesaw-jsql</artifactId>
        <version>0.43.1</version>
    </dependency>
    
    <!-- 데이터베이스 드라이버 (예: MySQL) -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.28</version>
    </dependency>
</dependencies>
```

## 2. 데이터베이스에서 데이터 로드하기

### 방법 1: SQL 쿼리 결과를 Table로 직접 로드

```java
import tech.tablesaw.api.Table;
import tech.tablesaw.io.jdbc.SqlResultSetReader;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class DbToCsv {
    public static void main(String[] args) throws Exception {
        // 데이터베이스 연결 설정
        String dbUrl = "jdbc:mysql://localhost:3306/your_database";
        String username = "your_username";
        String password = "your_password";
        
        // JDBC 연결 생성
        try (Connection connection = DriverManager.getConnection(dbUrl, username, password)) {
            // SQL 쿼리 실행
            String query = "SELECT * FROM your_table WHERE condition = true";
            Statement statement = connection.createStatement();
            ResultSet resultSet = statement.executeQuery(query);
            
            // ResultSet을 Tablesaw Table로 변환
            Table table = SqlResultSetReader.read(resultSet, "my_table");
            
            // 테이블 내용 확인
            System.out.println(table.print());
            
            // CSV로 저장
            table.write().csv("output.csv");
            
            System.out.println("CSV 파일이 성공적으로 생성되었습니다.");
        }
    }
}
```

### 방법 2: JDBC를 통해 데이터 로드 (더 유연한 방법)

```java
import tech.tablesaw.api.Table;
import tech.tablesaw.io.jdbc.SqlResultSetReader;

import java.sql.*;

public class DbToCsvAdvanced {
    public static void main(String[] args) {
        String dbUrl = "jdbc:mysql://localhost:3306/your_database";
        String user = "your_username";
        String pass = "your_password";
        
        try (Connection conn = DriverManager.getConnection(dbUrl, user, pass)) {
            // 파라미터화된 쿼리 사용 예제
            String sql = "SELECT id, name, age, salary FROM employees WHERE department = ?";
            
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, "IT");  // IT 부서 직원만 조회
            
            ResultSet rs = pstmt.executeQuery();
            
            // ResultSet을 Table로 변환
            Table employees = SqlResultSetReader.read(rs, "employees");
            
            // 데이터 확인
            System.out.println("Structure: " + employees.structure());
            System.out.println("First 10 rows:\n" + employees.first(10));
            
            // 데이터 처리 예: 연봉 5만 이상 필터링
            Table highEarners = employees.where(employees.doubleColumn("salary").isGreaterThan(50000));
            
            // CSV로 저장
            highEarners.write().csv("high_earners.csv");
            System.out.println("고액 연봉자 데이터가 high_earners.csv 파일로 저장되었습니다.");
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

## 3. 데이터 처리 후 CSV로 저장하기

Tablesaw를 사용하면 데이터를 쉽게 처리할 수 있습니다.

```java
import tech.tablesaw.api.Table;
import tech.tablesaw.io.jdbc.SqlResultSetReader;

import java.sql.*;

public class DataProcessingExample {
    public static void main(String[] args) throws SQLException {
        // 데이터베이스 연결 및 데이터 로드
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/your_db", "user", "pass");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM sales_data");
        Table sales = SqlResultSetReader.read(rs, "sales");
        
        // 데이터 처리
        // 1. 특정 열 선택
        Table selectedColumns = sales.select("date", "product", "amount", "region");
        
        // 2. 필터링: 금액이 1000 이상인 거래만
        Table highValueSales = selectedColumns.where(
            selectedColumns.doubleColumn("amount").isGreaterThanOrEqualTo(1000)
        );
        
        // 3. 지역별 평균 금액 계산
        Table avgByRegion = selectedColumns.summarize("amount", mean).by("region");
        
        // 4. 정렬: 금액 기준 내림차순
        highValueSales = highValueSales.sortDescendingOn("amount");
        
        // 처리된 데이터 CSV로 저장
        highValueSales.write().csv("high_value_sales.csv");
        avgByRegion.write().csv("average_by_region.csv");
        
        System.out.println("데이터 처리 및 CSV 저장 완료");
    }
}
```

## 4. 고급 기능 및 팁

1. **대용량 데이터 처리**:
   ```java
   // 청크 단위로 데이터 처리
   int chunkSize = 10000;
   Table bigTable = Table.create("Big Data");
   
   for (int offset = 0; ; offset += chunkSize) {
       ResultSet chunk = conn.createStatement().executeQuery(
           "SELECT * FROM large_table LIMIT " + chunkSize + " OFFSET " + offset
       );
       
       if (!chunk.next()) break;
       
       bigTable.append(SqlResultSetReader.read(chunk, "chunk_" + offset));
   }
   
   bigTable.write().csv("large_data.csv");
   ```

2. **CSV 저장 옵션 설정**:
   ```java
   // CSV 저장 옵션 설정
   table.write().csv(
       CsvWriteOptions.builder("custom_output.csv")
           .separator('|')          // 구분자 변경
           .header(true)            // 헤더 포함
           .escapeChar('\\')        // 이스케이프 문자
           .lineEnd("\r\n")         // 줄바꿈 문자
           .quoteChar('"')          // 인용 문자
           .build()
   );
   ```

3. **다양한 데이터베이스 지원**:
   - MySQL, PostgreSQL, Oracle 등 JDBC를 지원하는 모든 데이터베이스 사용 가능
   - 각 데이터베이스에 맞는 JDBC 드라이버만 추가하면 됨

## 5. 문제 해결

1. **메모리 부족 문제**:
   - 대용량 데이터는 청크 단위로 처리
   - `-Xmx` 옵션으로 JVM 힙 메모리 증가 (예: `-Xmx4G`)

2. **데이터 타입 불일치**:
   - Tablesaw가 자동으로 감지한 데이터 타입이 맞지 않을 경우 명시적 변환
   ```java
   Table table = SqlResultSetReader.read(rs, "table", 
       ColumnType.LOCAL_DATE,  // date_column은 날짜 타입으로
       ColumnType.DOUBLE,      // amount_column은 double 타입으로
       ColumnType.STRING);     // name_column은 문자열로
   ```

3. **CSV 인코딩 문제**:
   ```java
   table.write().usingOptions(
       CsvWriteOptions.builder(new File("output.csv"))
           .charset(StandardCharsets.UTF_8)  // UTF-8 인코딩 지정
           .build()
   );
   ```

이 가이드를 통해 Tablesaw를 사용하여 데이터베이스에서 데이터를 가져와 처리한 후 CSV 파일로 저장하는 전체 과정을 구현할 수 있습니다. 필요에 따라 데이터 처리 단계를 추가하거나 수정하여 사용하시면 됩니다.