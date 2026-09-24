/*
 * Copyright 2020 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package gift.dhamma.pali;

import android.app.SearchManager;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;



public class LauncherActivity
        extends com.google.androidbrowserhelper.trusted.LauncherActivity {
    

    

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // A text selection (ACTION_PROCESS_TEXT) arrives with the selected text in an extra and NO
        // data. The androidbrowserhelper base decides in its OWN onCreate whether to relaunch the
        // TWA or merely finish, and it only relaunches when the intent carries data or share data —
        // so a selection would silently do nothing (or just bring the app to the front). Turning it
        // into the site's ?q= URL here, before super.onCreate() reads the intent, makes it the same
        // kind of "open this page" launch as a shared link; getLaunchingUrl() below then hands that
        // URL over unchanged.
        Intent intent = getIntent();
        if (Intent.ACTION_PROCESS_TEXT.equals(intent.getAction())) {
            // getCharSequenceExtra, not getStringExtra: a selection arrives as a Spannable.
            CharSequence selected = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT);
            if (selected != null && selected.length() > 0) {
                intent.setData(Uri.parse("https://dict.dhamma.gift/?q=" + Uri.encode(selected.toString())));
            }
        } else if (Intent.ACTION_SEARCH.equals(intent.getAction())) {
            // A query from Android's system search ("Search in apps", res/xml/searchable.xml) or a
            // tapped suggestion from DgDictSuggestProvider. Same trap as the selection above: the
            // query arrives as an extra with NO data, and the base class only relaunches the TWA
            // when the intent carries data — so the URL is set here, before super.onCreate reads it.
            // A suggestion already carries the full ?q= URL and needs nothing.
            String query = intent.getStringExtra(SearchManager.QUERY);
            if (query != null && !query.trim().isEmpty()) {
                // Remembered here rather than in the provider: this is the only place that sees a
                // query the reader meant, and the provider offers these back as its recent list.
                DgDictSuggestProvider.rememberQuery(this, query);
                intent.setData(Uri.parse("https://dict.dhamma.gift/?q=" + Uri.encode(query)));
            }
        }
        super.onCreate(savedInstanceState);
        // Setting an orientation crashes the app due to the transparent background on Android 8.0
        // Oreo and below. We only set the orientation on Oreo and above. This only affects the
        // splash screen and Chrome will still respect the orientation.
        // See https://github.com/GoogleChromeLabs/bubblewrap/issues/496 for details.
        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.O) {
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
        } else {
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
        }
    }

@Override
protected Uri getLaunchingUrl() {
    // Get the original launch Url.
    Uri uri = super.getLaunchingUrl();

    // Handle shared text from share intent
    if (Intent.ACTION_SEND.equals(getIntent().getAction()) && getIntent().getType() != null && getIntent().getType().equals("text/plain")) {
        String sharedText = getIntent().getStringExtra(Intent.EXTRA_TEXT);
        if (sharedText != null) {
            uri = Uri.parse("https://dict.dhamma.gift/?q=" + Uri.encode(sharedText));
        }
    }

    // ACTION_SEARCH and a tapped suggestion need nothing here: the first gets its data set in
    // onCreate (before the base class decides whether to relaunch), the second arrives with the
    // full ?q= URL in its data and super.getLaunchingUrl() already returns it.

    return uri;
}
}
