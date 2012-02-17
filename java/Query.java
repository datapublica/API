import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.security.MessageDigest;

/*
 * Copyright (C) by Data Publica, All Rights Reserved.
 */

class Hasher {
    
    private static final char[] HEX_DIGITS = "0123456789abcdef".toCharArray();
    
    public static String digest(String algorithm, String input){
        try {
            MessageDigest messageDigest = MessageDigest.getInstance(algorithm);
            messageDigest.update(input.getBytes(), 0, input.length());
            
            byte[] digest = messageDigest.digest();
            
            return toString(digest, 0, digest.length);
            
        } catch (Exception x) {
            x.printStackTrace();
        }
        return null;
    }

    public static final String toString(byte[] ba, int offset, int length) {
        char[] buf = new char[length * 2];
        for (int i = 0, j = 0, k; i < length;) {
            k = ba[offset + i++];
            buf[j++] = HEX_DIGITS[(k >>> 4) & 0x0F];
            buf[j++] = HEX_DIGITS[k & 0x0F];
        }
        return new String(buf);
    }
}

public class Query {
    private String apiKey;
    private String passwd;
    private String dataRef;
    private String tableName;
    private String format;
    private Integer limit;
    private Integer offset;
    
    private String filters = null;
    
    
    /**
     * Initiates a query.  The four first paramets are mandatory, whereas the 
     * following are optionals.
     * @param apiKey
     * @param passwd
     * @param dataRef
     * @param tableName
     * @param format
     * @param limit
     * @param offset
     */
    public Query(String apiKey, String passwd, String dataRef, String tableName, String format, Integer limit,
                    Integer offset) {
        this.apiKey = apiKey;
        this.passwd = passwd;
        this.dataRef = dataRef;
        this.tableName = tableName;
        this.format = format;
        this.limit = limit;
        this.offset = offset;
        
        if( apiKey == null || passwd == null || dataRef == null || tableName == null) {
            throw new IllegalArgumentException("At least one of the mandatory parameters is missing");
        }
        
        if( format == null )
            this.format = "json";
        if( limit == null )
            this.limit = 50;
        if( offset == null )
            this.offset = 0;
        
    }
    
    /**
     * Adds filters instructions under the form of a string. 
     * This string must be compliant with Data Publica API specifications.
     * @param filtersContent 
     */
    public void addFilters(String filtersContent) {
        filters = filtersContent;
    }
    
    public String toURL(String domain) {
        if( domain == null ) {
            domain = "http://api.data-publica.com/v1/";
        }
        String s = sign( domain );
        
        return buildURL(domain, s);
    }
    
    public String sign(String domain) {
       String s = domain;
       
       s += dataRef + "/" + tableName + "/content";
       
       if(filters != null)
           s += ",filter=" + filters;
       
       s += ",format=" + format;
       s += ",key=" + apiKey;
       s += ",limit=" + limit;
       s += ",offset=" + offset;
       s += "," + passwd;
       
       return Hasher.digest("SHA-1", s);
    }
    
    private String buildURL(String domain, String signature) {
        String url = domain + dataRef + "/" + tableName + "/content?";
        String s = "";
        
        try {
            System.out.println(format);
            if(filters != null) {
                s += "filter=" + URLEncoder.encode(filters, "UTF-8");
                s += "&format=" + URLEncoder.encode(format, "UTF-8");
            }
            else
                s += "format=" + URLEncoder.encode(format, "UTF-8");
            s += "&key=" + URLEncoder.encode(apiKey, "UTF-8");
            s += "&limit=" + URLEncoder.encode(limit.toString(), "UTF-8");
            s += "&offset=" + URLEncoder.encode(offset.toString(), "UTF-8");
            s += "&signature=" + URLEncoder.encode(signature, "UTF-8");
        }
        catch(UnsupportedEncodingException e) {
            
        }
        url += s;
        
        return url;
    }
    
}
