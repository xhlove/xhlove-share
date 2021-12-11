import DashParser from './src/dash/parser/DashParser.js';
import DebugMock from './DebugMock.js';

import URLUtils from './src/streaming/utils/URLUtils.js';
import XlinkController from './src/streaming/controllers/XlinkController.js';
import Constants from './src/streaming/constants/Constants.js';

import * as fs from 'fs';
import {JSDOM as jsdom} from 'jsdom';

const context = {};
const urlUtils = URLUtils(context).getInstance();

// 第零步 链接配置

// 页面url
let href_url = "http://reference.dashif.org/dash.js/nightly/samples/dash-if-reference-player/index.html";
// 注意302的情况
let responseURL = "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd";
// mpd原始链接
let url = "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd";

let actualUrl, baseUri, manifest;

if (responseURL && responseURL !== url) {
    baseUri = urlUtils.parseBaseUrl(responseURL);
    actualUrl = responseURL;
} else {
    if (urlUtils.isRelative(url)) {
        url = urlUtils.resolve(url, href_url);
    }
    baseUri = urlUtils.parseBaseUrl(url);
}

// 第一步 转换mpd为合适的数据结构

let dashParser = DashParser(context).create({debug: new DebugMock()});

if (typeof window === 'undefined') {
    global.window = {
        performance: {
            now: function () {
                return Date.now();
            }
        },
        DOMParser:  new jsdom().window.DOMParser
    };
}

let __dirname = process.cwd();
let data = fs.readFileSync(__dirname + '/samples/dash/bbb_30fps.mpd', 'utf8');

let xlinkController = XlinkController(context).create({
    errHandler: null,
    dashMetrics: null,
    mediaPlayerModel: null,
    requestModifier: null,
    settings: null
});

manifest = dashParser.parse(data);

// 第二步 节点预处理

manifest.url = actualUrl || url;

// URL from which the MPD was originally retrieved (MPD updates will not change this value)
if (!manifest.originalUrl) {
    manifest.originalUrl = manifest.url;
}

// In the following, we only use the first Location entry even if many are available
// Compare with ManifestUpdater/DashManifestModel
if (manifest.hasOwnProperty(Constants.LOCATION)) {
    baseUri = urlUtils.parseBaseUrl(manifest.Location_asArray[0]);
    logger.debug('BaseURI set by Location to: ' + baseUri);
}

manifest.baseUri = baseUri;
manifest.loadedTime = new Date();
xlinkController.resolveManifestOnLoad(manifest);

console.log("manifest");
console.log(manifest);

// 第三步 转换链接 主要转换逻辑在 dashHandler

let dashHandler = DashHandler(context).create({
    streamInfo,
    type,
    timelineConverter,
    dashMetrics,
    mediaPlayerModel,
    baseURLController: config.baseURLController,
    errHandler,
    segmentsController,
    settings,
    boxParser,
    events: Events,
    eventBus,
    errors: Errors,
    debug: Debug(context).getInstance(),
    requestModifier: RequestModifier(context).getInstance(),
    dashConstants: DashConstants,
    constants: Constants,
    urlUtils: URLUtils(context).getInstance()
});

dashHandler.getInitRequest(mediaInfo, rep);

// dashHandler._getFragmentRequest

while (true){
    const representationInfo = getRepresentationInfo();
    let request;
    
    if (isNaN(bufferingTime) || (getType() === Constants.TEXT && !textController.isTextEnabled())) {
        console.log("break loop");
        break;
    }
    
    const useTime = shouldUseExplicitTimeForRequest;
    
    if (dashHandler) {
        const representation = representationController && representationInfo ? representationController.getRepresentationForQuality(representationInfo.quality) : null;
    
        if (useTime) {
            request = dashHandler.getSegmentRequestForTime(mediaInfo, representation, bufferingTime);
        } else {
            request = dashHandler.getNextSegmentRequest(mediaInfo, representation);
        }
    }
}