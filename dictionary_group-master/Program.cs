using System;
using System.Net;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;

namespace TCPClient
{

    public static class TCP
    {
        public static void Main()
        {
            string context = "The bat flew across the sky";
            string serverName = "https://0.0.0.0/"; // Server's temp name
           
            var data = new Dictionary<string, string>
            {
                {"word", "bat" },
                { "context", context},
                {"language", "ENG" }
            };

            WebClient webClient = new WebClient();
            byte[] resByte;
            string resString;
            byte[] reqString;
            string temp2 = serverName + "get_def";
            webClient.Headers["content-type"] = "application/json";
            reqString = Encoding.Default.GetBytes(JsonConvert.SerializeObject(data, Formatting.Indented));
            resByte = webClient.UploadData(temp2, "post", reqString);
            resString = Encoding.Default.GetString(resByte);
            Console.WriteLine(resString);
            webClient.Dispose();
            Console.ReadLine();
        }
    }
}