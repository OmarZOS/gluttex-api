'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {"main.dart.js": "247492315798ec597428b0b50355b514",
"version.json": "3c05c97582b8d30e71d7a024af411a53",
"canvaskit/skwasm.worker.js": "89990e8c92bcb123999aa81f7e203b1c",
"canvaskit/skwasm.wasm": "828c26a0b1cc8eb1adacbdd0c5e8bcfa",
"canvaskit/canvaskit.wasm": "e7602c687313cfac5f495c5eac2fb324",
"canvaskit/canvaskit.js": "26eef3024dbc64886b7f48e1b6fb05cf",
"canvaskit/canvaskit.js.symbols": "efc2cd87d1ff6c586b7d4c7083063a40",
"canvaskit/skwasm.js.symbols": "96263e00e3c9bd9cd878ead867c04f3c",
"canvaskit/chromium/canvaskit.wasm": "ea5ab288728f7200f398f60089048b48",
"canvaskit/chromium/canvaskit.js": "b7ba6d908089f706772b2007c37e6da4",
"canvaskit/chromium/canvaskit.js.symbols": "e115ddcfad5f5b98a90e389433606502",
"canvaskit/skwasm.js": "ac0f73826b925320a1e9b0d3fd7da61c",
"manifest.json": "07c0d08204cde88b1375b0fbde9335a3",
"flutter.js": "4b2350e14c6650ba82871f60906437ea",
"icons/Icon-512.png": "e30c0e3f6bbd22cdb2b1872544f2d354",
"icons/Icon-maskable-192.png": "d21fc4011dab3919d59c15c9581d6c16",
"icons/Icon-192.png": "99f98da49b954827186fb499d31d9bce",
"icons/Icon-maskable-512.png": "e30c0e3f6bbd22cdb2b1872544f2d354",
"assets/AssetManifest.json": "c268fd0afc3eb9d76ca6ea6d949f7bcc",
"assets/NOTICES": "3fb625107f86850eacf74c5db1062bd0",
"assets/AssetManifest.bin": "78c0da6287f0e4da4e98d6a3873d1b39",
"assets/FontManifest.json": "5a32d4310a6f5d9a6b651e75ba0d7372",
"assets/AssetManifest.bin.json": "fc96a0a7385ccea912e2ec27647a87b6",
"assets/shaders/ink_sparkle.frag": "ecc85a2e95f5e9f53123dcaf8cb9b6ce",
"assets/fonts/MaterialIcons-Regular.otf": "fc3f94eb21111e3cf1f2537924e75baa",
"assets/packages/font_awesome_flutter/lib/fonts/fa-solid-900.ttf": "e591964b283a298604b5756792f6ada8",
"assets/packages/font_awesome_flutter/lib/fonts/fa-regular-400.ttf": "323ef09c7ab8537049fad3c890c61600",
"assets/packages/font_awesome_flutter/lib/fonts/fa-brands-400.ttf": "fd198db8f095268c7308bc7cd3bc2acf",
"assets/packages/medicom_catalog/assets/icons/10.svg": "a7f6054a818e816cc8e73ee1376ef864",
"assets/packages/medicom_catalog/assets/icons/6.svg": "5cc1a45f579643085c59444ede00edef",
"assets/packages/medicom_catalog/assets/icons/add_to_cart.svg": "0eb1a5e481ee24dba9de843a9dacdde1",
"assets/packages/medicom_catalog/assets/icons/1.svg": "afe936f758f18f420732e8341d760da2",
"assets/packages/medicom_catalog/assets/icons/8.svg": "d1d6c8d2587044d91df65aea244a7eb1",
"assets/packages/medicom_catalog/assets/icons/5.svg": "b35c5048f26eb7a23359a10e05272947",
"assets/packages/medicom_catalog/assets/icons/3.svg": "63e4290ae494fe2371fd631599f8f147",
"assets/packages/medicom_catalog/assets/icons/7.svg": "59575e831f02eac7de7888649e2925d3",
"assets/packages/medicom_catalog/assets/icons/cart.svg": "fd320d807686c8432b2e449a583296b1",
"assets/packages/medicom_catalog/assets/icons/0.svg": "c9a87be3e515026c27e4ec576713bb3f",
"assets/packages/medicom_catalog/assets/icons/9.svg": "cd56078e67d47de23b68bb3064dd8347",
"assets/packages/medicom_catalog/assets/icons/heart_enabled.svg": "0aa011cfbdb6278b9bdef4d42f9bd413",
"assets/packages/medicom_catalog/assets/icons/2.svg": "bb47353b7af1a9c45cf20792f9bfefe6",
"assets/packages/medicom_catalog/assets/icons/back.svg": "1b13e0b59c27ec75d6f5051e5d66e8d9",
"assets/packages/medicom_catalog/assets/icons/4.svg": "2303ec0525924aea564b4c2f530aa0ad",
"assets/packages/medicom_catalog/assets/icons/heart_disabled.svg": "fea386c56ee681deb2dc5ba0a78df5c8",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "685d2f437dc9ca678b36e7ab91af2ce2",
"assets/packages/gluttex_login/assets/images/logo.svg": "4a45c240e6582a334b99a1a655a17d40",
"assets/packages/gluttex_chef/assets/ingredient_svg/33.svg": "a2afd0073fb59d48b226db4aaf3bc7c6",
"assets/packages/gluttex_chef/assets/ingredient_svg/10.svg": "a5646435f7dcf26faec57787a26a95c5",
"assets/packages/gluttex_chef/assets/ingredient_svg/38.svg": "f289dad93cc70753a7905fa8d4c63885",
"assets/packages/gluttex_chef/assets/ingredient_svg/22.svg": "7cc6f83b8f7126ff11009250d11c6a7e",
"assets/packages/gluttex_chef/assets/ingredient_svg/14.svg": "bcbfc6bb3973c744567989254c466a97",
"assets/packages/gluttex_chef/assets/ingredient_svg/51.svg": "c3c1f32c965f9b5012a84fbff73a2660",
"assets/packages/gluttex_chef/assets/ingredient_svg/52.svg": "8df0368af32a95eef9eb3e2217d0e0fd",
"assets/packages/gluttex_chef/assets/ingredient_svg/53.svg": "e71071aac0b9dfa99d50f260000beda3",
"assets/packages/gluttex_chef/assets/ingredient_svg/29.svg": "2a14bda1005d600275861935a9a877d3",
"assets/packages/gluttex_chef/assets/ingredient_svg/56.svg": "a2e4cbd7add2798cf0e6d1465e5fce18",
"assets/packages/gluttex_chef/assets/ingredient_svg/6.svg": "abbfad7412a2dc90645c794838855b47",
"assets/packages/gluttex_chef/assets/ingredient_svg/46.svg": "c3c1f32c965f9b5012a84fbff73a2660",
"assets/packages/gluttex_chef/assets/ingredient_svg/36.svg": "f289dad93cc70753a7905fa8d4c63885",
"assets/packages/gluttex_chef/assets/ingredient_svg/47.svg": "c3c1f32c965f9b5012a84fbff73a2660",
"assets/packages/gluttex_chef/assets/ingredient_svg/26.svg": "3e7cb9f2ba63e96085c77e27a7b9e569",
"assets/packages/gluttex_chef/assets/ingredient_svg/49.svg": "e71071aac0b9dfa99d50f260000beda3",
"assets/packages/gluttex_chef/assets/ingredient_svg/43.svg": "21823feeaa9a6676aca62e0a217a3dc0",
"assets/packages/gluttex_chef/assets/ingredient_svg/55.svg": "21f5b64e75cf9fd398fb209e793879f3",
"assets/packages/gluttex_chef/assets/ingredient_svg/24.svg": "a2e4cbd7add2798cf0e6d1465e5fce18",
"assets/packages/gluttex_chef/assets/ingredient_svg/25.svg": "ee7609a8b90752674fc60c9c802af796",
"assets/packages/gluttex_chef/assets/ingredient_svg/1.svg": "e22db50161dc4c13fed99b0a6b5a102b",
"assets/packages/gluttex_chef/assets/ingredient_svg/59.svg": "902278f9e0a3630dca688451b44398b9",
"assets/packages/gluttex_chef/assets/ingredient_svg/17.svg": "509fe60a4ae572fb23e210e3772d0510",
"assets/packages/gluttex_chef/assets/ingredient_svg/11.svg": "a467faf7ef1a200a95dfe1918359748e",
"assets/packages/gluttex_chef/assets/ingredient_svg/21.svg": "726c4fd40fbe50b6e251d5ee27c27d7c",
"assets/packages/gluttex_chef/assets/ingredient_svg/8.svg": "6a6a85a9619284514d5b819817bac13d",
"assets/packages/gluttex_chef/assets/ingredient_svg/18.svg": "5a00a538ff6c03b99a03818ff57c224a",
"assets/packages/gluttex_chef/assets/ingredient_svg/32.svg": "62090bdc37f85d444fcd2f0f738bfef9",
"assets/packages/gluttex_chef/assets/ingredient_svg/5.svg": "15657b642043cd28ef98dcec0eb3afaf",
"assets/packages/gluttex_chef/assets/ingredient_svg/3.svg": "8d55a37297ac0681cbd32bd6c5f4cf20",
"assets/packages/gluttex_chef/assets/ingredient_svg/7.svg": "a2e4cbd7add2798cf0e6d1465e5fce18",
"assets/packages/gluttex_chef/assets/ingredient_svg/23.svg": "7cc6f83b8f7126ff11009250d11c6a7e",
"assets/packages/gluttex_chef/assets/ingredient_svg/13.svg": "3bea9a197759204e21e1dcc571e68429",
"assets/packages/gluttex_chef/assets/ingredient_svg/50.svg": "c3c1f32c965f9b5012a84fbff73a2660",
"assets/packages/gluttex_chef/assets/ingredient_svg/34.svg": "1c6807ef4192142f4ac211e1fbb3964e",
"assets/packages/gluttex_chef/assets/ingredient_svg/9.svg": "47266498b06f173a821cc4e998dc8215",
"assets/packages/gluttex_chef/assets/ingredient_svg/30.svg": "3ef292cde0f2e91d94f86dbbd70abfcd",
"assets/packages/gluttex_chef/assets/ingredient_svg/37.svg": "f289dad93cc70753a7905fa8d4c63885",
"assets/packages/gluttex_chef/assets/ingredient_svg/61.svg": "902278f9e0a3630dca688451b44398b9",
"assets/packages/gluttex_chef/assets/ingredient_svg/12.svg": "6f7894894e2f345fc9329880a02f8728",
"assets/packages/gluttex_chef/assets/ingredient_svg/2.svg": "448deaa961dda70f647dc08075614efe",
"assets/packages/gluttex_chef/assets/ingredient_svg/20.svg": "a7664ace2d8632bf424123cc4f9aacdf",
"assets/packages/gluttex_chef/assets/ingredient_svg/42.svg": "21823feeaa9a6676aca62e0a217a3dc0",
"assets/packages/gluttex_chef/assets/ingredient_svg/39.svg": "f289dad93cc70753a7905fa8d4c63885",
"assets/packages/gluttex_chef/assets/ingredient_svg/16.svg": "ebc3bf423bb35cd08b2e8f340023abd0",
"assets/packages/gluttex_chef/assets/ingredient_svg/4.svg": "06ad43dfb66f0aaa54f8b7c39556d953",
"assets/packages/gluttex_chef/assets/ingredient_svg/48.svg": "e71071aac0b9dfa99d50f260000beda3",
"assets/packages/gluttex_chef/assets/ingredient_svg/15.svg": "bcbfc6bb3973c744567989254c466a97",
"assets/packages/gluttex_chef/assets/ingredient_svg/62.svg": "902278f9e0a3630dca688451b44398b9",
"assets/packages/gluttex_chef/assets/ingredient_svg/41.svg": "21823feeaa9a6676aca62e0a217a3dc0",
"assets/packages/gluttex_chef/assets/ingredient_svg/40.svg": "21823feeaa9a6676aca62e0a217a3dc0",
"assets/packages/gluttex_chef/assets/ingredient_svg/19.svg": "ac5ee3bf6029359aad323466cd1c8bd1",
"assets/packages/gluttex_chef/assets/ingredient_svg/27.svg": "34c434d789efff068cc18ea42889d49e",
"assets/packages/gluttex_chef/assets/ingredient_svg/28.svg": "e71071aac0b9dfa99d50f260000beda3",
"assets/packages/gluttex_chef/assets/ingredient_svg/35.svg": "1c6807ef4192142f4ac211e1fbb3964e",
"assets/packages/gluttex_chef/assets/ingredient_svg/31.svg": "51bbb32a64128ee42223aff1e19331b1",
"assets/packages/gluttex_chef/assets/ingredient_svg/58.svg": "902278f9e0a3630dca688451b44398b9",
"assets/packages/gluttex_chef/assets/ingredient_svg/57.svg": "902278f9e0a3630dca688451b44398b9",
"assets/packages/gluttex_chef/assets/ingredient_svg/45.svg": "21823feeaa9a6676aca62e0a217a3dc0",
"assets/packages/gluttex_chef/assets/ingredient_svg/60.svg": "902278f9e0a3630dca688451b44398b9",
"assets/packages/gluttex_chef/assets/ingredient_svg/54.svg": "21f5b64e75cf9fd398fb209e793879f3",
"assets/packages/gluttex_chef/assets/ingredient_svg/44.svg": "1c6807ef4192142f4ac211e1fbb3964e",
"assets/packages/gluttex_chef/assets/icons/10.svg": "59575e831f02eac7de7888649e2925d3",
"assets/packages/gluttex_chef/assets/icons/14.svg": "13c7f0798e432db4db71caaed30b91d8",
"assets/packages/gluttex_chef/assets/icons/6.svg": "2303ec0525924aea564b4c2f530aa0ad",
"assets/packages/gluttex_chef/assets/icons/1.svg": "3d0fb6be3c3eb5b848d6322379a3aa8b",
"assets/packages/gluttex_chef/assets/icons/17.svg": "6d827d7b9d6eeace5ae9682333b50246",
"assets/packages/gluttex_chef/assets/icons/11.svg": "5cc1a45f579643085c59444ede00edef",
"assets/packages/gluttex_chef/assets/icons/8.svg": "23e86e7e094338718fc846afc6d0cb48",
"assets/packages/gluttex_chef/assets/icons/18.svg": "1fc464e5a538fecc0624235308cbb3e1",
"assets/packages/gluttex_chef/assets/icons/5.svg": "3445526d7de4922c2e54befaefbce7ff",
"assets/packages/gluttex_chef/assets/icons/3.svg": "7b360a67780faa5636e24c9e7e7dcef2",
"assets/packages/gluttex_chef/assets/icons/7.svg": "9282612f333d36e386e529d520b36f13",
"assets/packages/gluttex_chef/assets/icons/0.svg": "b4c3fa126dc058f06e482705f652934e",
"assets/packages/gluttex_chef/assets/icons/13.svg": "fbba35a7f3617fdb3737bea524979342",
"assets/packages/gluttex_chef/assets/icons/9.svg": "afe936f758f18f420732e8341d760da2",
"assets/packages/gluttex_chef/assets/icons/12.svg": "df12c17f1f441f985ec7c6bf2d15f003",
"assets/packages/gluttex_chef/assets/icons/2.svg": "f73784424d46c6a6abc4ac1fa8451fa1",
"assets/packages/gluttex_chef/assets/icons/20.svg": "8b27be4769100decb8ed0beb1ce97de8",
"assets/packages/gluttex_chef/assets/icons/16.svg": "3f4935bddbd794e71cd2f4bce7896a48",
"assets/packages/gluttex_chef/assets/icons/4.svg": "8a015116d30deb3f0d43cb0092d4f890",
"assets/packages/gluttex_chef/assets/icons/15.svg": "ba99f758bb08c52a7baff5bc40069ede",
"assets/packages/gluttex_chef/assets/icons/19.svg": "c9b7a451d37fb46760b24f4f32661469",
"assets/packages/gluttex_play/assets/images/pizza.svg": "525602a18d25ba804d105671180b5914",
"assets/packages/gluttex_play/assets/images/coming_soon.jpeg": "f77982c97f9c3913070235abc09baf32",
"assets/packages/gluttex_play/assets/images/watermelon.svg": "f8f18a5c62ded108f558d17b18bf1fea",
"assets/packages/gluttex_play/assets/images/banana.svg": "e651cbdd813118971988ea3f33c27a74",
"assets/packages/gluttex_play/assets/images/donut.svg": "1eb70366157352b82e954725f810c507",
"assets/packages/gluttex_play/assets/images/hamburger.svg": "2b5e04da23cf980b1b781a93ecbf0fc6",
"assets/packages/gluttex_play/assets/images/quiz.jpg": "d030a834516c05d549a619dd0730c344",
"assets/packages/gluttex_play/assets/images/strawberry.svg": "2e9ce3f9725d5fba9442b41a0fc1d712",
"assets/packages/gluttex_play/assets/images/taco.svg": "3f373e89edfbd39ef97647bd1e6e9e30",
"assets/packages/gluttex_play/assets/images/fish.svg": "c4ba820ebba5310819739a82699567da",
"assets/packages/gluttex_play/assets/images/apple_pie.svg": "4507849a6871e03d3c630acf34b31cdb",
"assets/packages/gluttex_play/assets/images/snake.jpg": "0fb370846d04a438b15a305187dba8ba",
"assets/packages/gluttex_play/assets/images/bread.svg": "e65aa2b54326f88b9f89d57c269c7e35",
"assets/packages/gluttex_play/assets/images/croissant.svg": "29d419a131c93549f89451a6eea128e8",
"assets/packages/gluttex_localiser/assets/icons/6.svg": "1393460e2343d5bd42a3766a34e65d16",
"assets/packages/gluttex_localiser/assets/icons/1.svg": "c9a87be3e515026c27e4ec576713bb3f",
"assets/packages/gluttex_localiser/assets/icons/5.svg": "fa12ccd05a032f4de8edb348173da6b5",
"assets/packages/gluttex_localiser/assets/icons/3.svg": "5b7c1e45a1d39ce5528bd047d965ffd3",
"assets/packages/gluttex_localiser/assets/icons/0.svg": "067090ddfbd55fad7e407238d7f1918c",
"assets/packages/gluttex_localiser/assets/icons/2.svg": "bb7c38d2ff2cd5a54d0b6d3cd105aa7d",
"assets/packages/gluttex_localiser/assets/icons/4.svg": "1e6ea8ee3959d0a505a286f003737978",
"assets/packages/gluttex_home/assets/images/logo.png": "2b24546564fb2cef829626b891cfa04a",
"assets/packages/gluttex_home/assets/docs/terms_ar.pdf": "5b9061ade6ec087d3dd2156cccf4b6ac",
"assets/packages/gluttex_home/assets/docs/policy_en.pdf": "8f12af00b08cca1fae7086811786fb6e",
"assets/packages/gluttex_home/assets/docs/terms_en.pdf": "bbd70808d104a871300cad728295692e",
"assets/packages/gluttex_home/assets/docs/terms_fr.pdf": "3c4c5a14f5055078bca1d00f092477f9",
"assets/packages/gluttex_home/assets/docs/policy_ar.pdf": "50d2f0f4f5d9a7b7abafc279367e5269",
"assets/packages/gluttex_home/assets/docs/policy_fr.pdf": "810e9aa5d1b75c7babdf4c0d97b36bab",
"flutter_bootstrap.js": "0568d5aaab3090df6e0dd35b4b8c4c0c",
"index.html": "02ed65fadefa7177c6756ab7dbc5d3fb",
"/": "02ed65fadefa7177c6756ab7dbc5d3fb",
"favicon.png": "99f98da49b954827186fb499d31d9bce"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"flutter_bootstrap.js",
"assets/AssetManifest.bin.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
