# Streaming failover solution for Elemental encoder using S3 bucket

## What problem does this solve?
Suppose you have two Elemental encoders on-premises for a live streaming event, both handling the same video stream with output locking (sync at frame level) and output video manifest (.m3u8) and segment files (.ts) into different folders of same S3 bucket. You want to ensure if one encoder DOWN the live streaming at client side can continue seamlessly with the secondary/failover encoder.
The solution makes use of [HLS redundant streams](https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/StreamingMediaGuide/UsingHTTPLiveStreaming/UsingHTTPLiveStreaming.html#//apple_ref/doc/uid/TP40008332-CH102-SW22), which is a feature of Apple HLS's standard spec. This feature allows you to define multiple HLS renditions in your manifest that have identical characteristics, other than the URL which they point to, allowing the player to treat these as a redundant set, for failover purposes. In the HLS master manifest, it looks something like this:
```
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=200000, RESOLUTION=720x480
http://ALPHA.mycompany.com/lo/prog_index.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=200000, RESOLUTION=720x480
http://BETA.mycompany.com/lo/prog_index.m3u8
 
#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=500000, RESOLUTION=1920x1080
http://ALPHA.mycompany.com/md/prog_index.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=500000, RESOLUTION=1920x1080
http://BETA.mycompany.com/md/prog_index.m3u8
``` 
The solution consists of a Lambda function that will be triggered when the primary manifest (.m3u8) is uploaded and the Lambda will generate an index.m3u8 that contains both primary and failover sub-manifests.

## How to deploy the solution?

1. Ensure AWS SAM is installed in your workstation.
2. Run the following commands to deploy the S3 bucket and Lambda function into your AWS account:
   ```bash
   sam build
   sam deploy -g
   ```
3. Goto the CloudFormation stack in AWS Console, goto the stack created by SAM, and under the "Resources" tab find the S3 bucket created.
4. Goto the S3 bucket, create two folders in the bucket:
   - primary/
   - failover/
5. You can goto S3 bucket event notification setting, and see that there is an event trigger already configured for all S3 object creation events that got prefix "primary/" and suffix ".m3u8".
6. Now in your primary Elemental encoder output the stream to the S3 bucket's "primary/" folder, in your failover encoder output the stream to "failover/".
7. After streaming started, you will see an "index.m3u8" created in the root of S3 bucket, set your video player to use this file to start playing.
8. Always suggested to use CloudFront CDN and point to the S3 bucket with OAI for video streaming.

## Resources

To learn more on the HLS redundant stream feature and its supported players, you can have a look at this good blog from mux.com: [https://mux.com/blog/survive-cdn-failures-with-redundant-streams/](https://mux.com/blog/survive-cdn-failures-with-redundant-streams/)
