package foursquare;

import javax.json.*;
import java.io.*;
import java.net.*;
import java.sql.*;
import java.sql.DriverManager;

/**
 * Created by qixiao on 4/7/17.
 */
public class Category {
    private static int count;
    public static void main(String[] args) throws Exception {
        URL category = new URL("https://api.foursquare.com/v2/venues/categories?" +
                "oauth_token=HDAXFHOB4HJGBGG3GLMM5FRB5MNMJT13U15UUDM0132Y4MRN&v=20170324");

        /*
        URLConnection yc = category.openConnection();
        BufferedReader in = new BufferedReader(new InputStreamReader(
                yc.getInputStream()));
        String inputLine;
        while ((inputLine = in.readLine()) != null) {
            System.out.println(inputLine);
        }
        in.close();
        */

        try (InputStream is = category.openStream();
             JsonReader rdr = Json.createReader(is);
             Connection conn =DriverManager.getConnection(
             "jdbc:mysql://localhost:3306/foursquare?useSSL=false", "qi", "1234@Abcd");
             Statement stmt = conn.createStatement()) {

            JsonObject obj = rdr.readObject();
            JsonObject response = obj.getJsonObject("response");
            JsonArray categories = response.getJsonArray("categories");

            // first level main & sub relationship will be inserted into mainCategory table
            // second and more levels will be inserted into subCategory table
            count = 0;
            for(int i = 0; i < categories.size(); i++) {
                JsonObject categories_obj = categories.getJsonObject(i);
                String main_category = categories_obj.getString("name");

                JsonArray categories_array = categories_obj.getJsonArray("categories");

                getCategoryHierarchy(categories_array, main_category, "mainCategory", stmt);
                /*
                for(int j = 0; j < categories_array.size(); j++) {
                    JsonObject temp_obj1 = categories_array.getJsonObject(j);
                    String sub_category = temp_obj1.getString("name");
                    System.out.println(main_category + "\t:" + sub_category);

                    String query = "insert into category values (" + "\""+ main_category + "\"" + ", "
                            +"\"" + sub_category + "\"" + ")";
                    stmt.executeUpdate(query);

                    JsonArray subcategories_array = temp_obj1.getJsonArray("categories");
                    for (int k = 0; k < subcategories_array.size(); k++) {
                        JsonObject temp_obj2 = subcategories_array.getJsonObject(k);
                        String sub_sub_category = temp_obj2.getString("name");
                        System.out.println(sub_category + "\t:" + sub_sub_category);

                        query = "insert into category values (\"" + sub_category + "\",\" " + sub_sub_category + "\")";
                        stmt.executeUpdate(query);
                    }
                }
                */
            }
            System.out.println("count: " + count);
        }
    }

    private static void getCategoryHierarchy(JsonArray categories, String main_category,
                                             String table_name, Statement stmt) throws Exception {
        for(int i = 0; i < categories.size(); i++) {
            JsonObject categories_obj = categories.getJsonObject(i);
            String sub_category = categories_obj.getString("name");

            String query = "insert into " + table_name + " values (\"" + main_category + "\",\"" + sub_category + "\")";
            stmt.executeUpdate(query);
            count++;

            JsonArray subcategories_array = categories_obj.getJsonArray("categories");
            getCategoryHierarchy(subcategories_array, sub_category, "subCategory", stmt);
        }
    }
}