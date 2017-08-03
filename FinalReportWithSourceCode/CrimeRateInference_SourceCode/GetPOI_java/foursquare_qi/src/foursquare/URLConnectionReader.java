package foursquare;

import javax.json.*;
import java.net.*;
import java.io.*;
import java.sql.*;
import java.util.concurrent.TimeUnit;


/**
 * Created by qixiao on 3/24/17.
 */
public class URLConnectionReader {
    private static double chicago_lat_min = 41.644543;    // down
    private static double chicago_lat_max = 42.023039;    // up
    private static double chicago_lon_min = -87.940114;   // left
    private static double chicago_lon_max = -87.524137;   // right
    private static double chicago_delta_lat = (chicago_lat_max - chicago_lat_min) / 100;
    private static double chicago_delta_lon = (chicago_lon_max - chicago_lon_min) / 100;

    //global start time;
    //global request count;
    private static long startTime;
    private static int requestCount = 0;

    public static void main(String[] args) throws Exception {
        
        //System.out.println(distance(41.645869,-87.526205,42.010165,-87.932700,"K"));

        // set start time
        startTime = System.currentTimeMillis();
        System.out.println("start: " + startTime);

        //poi(chicago_lat_min, chicago_lat_max, chicago_lon_min, chicago_lon_max,100,100);
        //poi(chicago_lat_min, chicago_lat_max - 25 * chicago_delta_lat, chicago_lon_min, chicago_lon_max,75,100);
        poi(chicago_lat_min, chicago_lat_max - 93 * chicago_delta_lat, chicago_lon_min, chicago_lon_max,7,100);
    }


    private static void poi(double lat_min, double lat_max, double lon_min, double lon_max, int row, int col) throws Exception{
        double delta_lon = (lon_max - lon_min) / col;
        double delta_lat = (lat_max - lat_min) / row;
        for (int i = 0; i < row; i++) {
            System.out.println("row #: " + i + "\t" + System.currentTimeMillis() + "\t count: " + requestCount);
            for (int j = 0; j < col; j++) {
                // (lat1,lon1) is upper left corner, (lat2,lon2) is lower right corner
                double lat1 = lat_max - i * delta_lat;
                double lon1 = lon_min + j * delta_lon;
                double lat2 = lat1 - delta_lat;
                double lon2 = lon1 + delta_lon;

                double radius = 0.5 * 1000 * distance(lat1,lon1,lat2,lon2,"K");  // unit is meters
                //System.out.println("radius: " + radius);
                double lat_mid = lat1 - 0.5 * delta_lat;
                double lon_mid = lon1 + 0.5 * delta_lon;

                // if duration < 1hr, count < 4999, explore url
                // else if duration < 1hr, count >= 4999, sleep until 1hr
                // else if duration > 1hr, reset start time to now, reset count to 0
                long now = System.currentTimeMillis();
                if ((now - startTime) < 3600000) {
                    if (requestCount >= 4998) {
                        long wait = 3600000 - (now - startTime);
                        try {
                            TimeUnit.MILLISECONDS.sleep(wait);
                            System.out.println("sleep for " + wait);
                            startTime = System.currentTimeMillis();
                            requestCount = 0;
                        } catch (InterruptedException e) {
                            System.out.println("sleep is interrupted!");
                        }
                    }
                } else {
                    System.out.println("a new hour start!");
                    startTime = System.currentTimeMillis();
                    requestCount = 0;
                }

                URL explore = new URL("https://api.foursquare.com/v2/venues/explore?ll=" +
                        Double.toString(lat_mid) + "," + Double.toString(lon_mid) +
                        //"&client_id=B0FPN1EMAP5CNMYDFHBHLRHA51AOEK2HNYERXPQKPTWBTIRF" +
                        "&client_id=WUVLK1LZL5XM3HQVKIYHNM4CAUMRHVAXEWB3LZU2MCO5WXP2" +
                        //"&client_secret=IKRJJJ4S5OBKY5YXVQRUU2UBOXSH321UDBGHKFS0YXPSMPC2" +
                        "&client_secret=GEY31LO5AH0MOB54NW4S1DCYYKB130HMOG3ZO4BUZT5FDUTC" +
                        "&v=20170101" +
                        "&m=foursquare" +
                        "&limit=50" +
                        "&radius=" + Double.toString(radius));

                requestCount++;

                try (InputStream is = explore.openStream();
                     JsonReader rdr = Json.createReader(is);
                     Connection conn = DriverManager.getConnection(
                             "jdbc:mysql://localhost:3306/foursquare?useSSL=false", "qi", "1234@Abcd");
                     Statement stmt = conn.createStatement()) {

                    JsonObject obj = rdr.readObject();
                    JsonObject response = obj.getJsonObject("response");
                    JsonArray groups = response.getJsonArray("groups");
                    JsonObject groups_obj = groups.getJsonObject(0);
                    JsonArray items = groups_obj.getJsonArray("items");
                    //System.out.println("result size: " + items.size());

                    if (items.size() < 50) {
                        for (JsonObject item : items.getValuesAs(JsonObject.class)) {

                            JsonObject venue = item.getJsonObject("venue");
                            String name = venue.getString("name");
                            JsonObject location = venue.getJsonObject("location");
                            JsonNumber lat = location.getJsonNumber("lat");
                            JsonNumber lng = location.getJsonNumber("lng");
                            JsonArray categories = venue.getJsonArray("categories");
                            JsonObject category_obj = categories.getJsonObject(0);
                            String sub_category = category_obj.getString("name");
                            //System.out.println(name + "\t" + lat.toString() + "\t" + lng.toString() +
                                   // "\t" + sub_category);

                            String main_category = findMainCategory(sub_category, stmt);
                            //System.out.println(main_category);


                            // insert ignore: no duplicate rows
                            String query = "insert ignore into poi values(" + Double.parseDouble(lat.toString()) + ","
                                    + Double.parseDouble(lng.toString()) + "," + "\"" + main_category + "\"" + ")" ;
                            stmt.executeUpdate(query);


                        }
                    } else {      // query result reaches limit of 50, need to further divide search area into smaller range
                        poi(lat2, lat1, lon1, lon2, 5, 5);
                    }
                }
            }
        }

    }

    private static String findMainCategory(String sub_category, Statement stmt) throws Exception{
        String result = null;
        String query = "select main_category from mainCategory where main_category=" + "\"" + sub_category + "\"";
        ResultSet rset = stmt.executeQuery(query);
        if (rset.next()) {
            result = rset.getString("main_category");
        } else {
            query = "select main_category from mainCategory where sub_category=" + "\"" + sub_category + "\"";
            rset = stmt.executeQuery(query);
            if (rset.next()) {
                result = rset.getString("main_category");
            } else {
                String tempsub = null;
                rset = null;
                do {
                    if (tempsub == null) {
                        tempsub = sub_category;
                    } else {
                        tempsub = rset.getString("main_category");
                    }
                    query = "select main_category from subCategory where sub_category=" + "\"" + tempsub + "\"";
                    rset = stmt.executeQuery(query);
                }while(rset.next());

                query = "select main_category from mainCategory where sub_category=" + "\"" + tempsub + "\"";
                rset = stmt.executeQuery(query);
                rset.next();
                result = rset.getString("main_category");
            }
        }

        assert (result != null);
        return result;
        /*
        String query = "select main_category from category where main_category=" + "\"" + sub_category + "\"";
        ResultSet rset = stmt.executeQuery(query);
        String result = null;
        // sometimes sub_category from poi is actually the main_category
        if (rset.next()){
            query = "select main_category from category where sub_category=" + "\"" + sub_category + "\"";
            rset = stmt.executeQuery(query);
            if (rset.next()) {
                result = rset.getString("main_category");
            } else {
                result = sub_category;
            }

        } else {
            query = "select main_category from category where sub_category=" + "\"" + sub_category + "\"";
            rset = stmt.executeQuery(query);
            //assert(rset.next());
            rset.next();
            result = rset.getString("main_category");
            // the category hierarchy is up to 3 layers
            query = "select main_category from category where sub_category=" + "\"" + result + "\"";
            rset = stmt.executeQuery(query);
            if (rset.next()) {
                result = rset.getString("main_category");
            }
        }

        assert(result != null);
        return result;
        */
    }

    /*
        Calculate distance between two GPS coordinates. Passed to function:                                                    :*/
    /*::    lat1, lon1 = Latitude and Longitude of point 1 (in decimal degrees)  :*/
    /*::    lat2, lon2 = Latitude and Longitude of point 2 (in decimal degrees)  :*/
    /*::    unit = the unit you desire for results                               :*/
    /*::           where: 'M' is statute miles (default)                         :*/
    /*::                  'K' is kilometers                                      :*/
    /*::                  'N' is nautical miles
     */

    private static double distance(double lat1, double lon1, double lat2, double lon2, String unit) {
        double theta = lon1 - lon2;
        double dist = Math.sin(deg2rad(lat1)) * Math.sin(deg2rad(lat2))
                + Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * Math.cos(deg2rad(theta));
        dist = Math.acos(dist);
        dist = rad2deg(dist);
        dist = dist * 60 * 1.1515;
        if (unit == "K") {
            dist = dist * 1.609344;
        } else if (unit == "N") {
            dist = dist * 0.8684;
        }

        return (dist);
    }


    /*
    This function converts decimal degrees to radians
     */
    private static double deg2rad(double deg) {
        return (deg * Math.PI / 180.0);
    }

    /*
    This function converts radians to decimal degrees
     */
    private static double rad2deg(double rad) {
        return (rad * 180 / Math.PI);
    }
}
