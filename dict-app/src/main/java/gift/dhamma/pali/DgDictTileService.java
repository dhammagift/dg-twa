package gift.dhamma.pali;

import android.app.PendingIntent;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.service.quicksettings.TileService;

/**
 * The dictionary in the Quick Settings shade: one tap from inside any app, with no launcher, no
 * browser tab and no share chooser in between.
 *
 * It carries no logic of its own. The tap builds the same VIEW intent the launcher shortcut and the
 * auto-verified link filter produce — LauncherActivity reads the URL straight off the intent and
 * opens the Trusted Web Activity there — so the tile, a shared link and a tapped dhamma.gift URL all
 * arrive through one path.
 *
 * The tile is invisible until the reader adds it: pull the shade down, edit the tiles, drag
 * "Dhamma.gift dictionary" into the panel. That is Android's rule for every app, not something an
 * app can skip.
 */
public class DgDictTileService extends TileService {

    // What the tile opens: the site's start page. "/?source=pwa" would be the installed-PWA start
    // URL, but a tile tap is not an install, and the plain root keeps the same ?q= and routing
    // handling every other entry point uses.
    private static final String URL = "https://dict.dhamma.gift/";

    @Override
    @SuppressWarnings("deprecation") // startActivityAndCollapse(Intent) below API 34
    public void onClick() {
        Intent intent = new Intent(this, LauncherActivity.class);
        intent.setAction(Intent.ACTION_VIEW);
        intent.setData(Uri.parse(URL));
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            // API 34 deprecated the Intent overload; the PendingIntent form is the supported one
            // there (and is what a tile must use to be allowed to start an activity at all).
            PendingIntent pending = PendingIntent.getActivity(this, 0, intent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            startActivityAndCollapse(pending);
        } else {
            startActivityAndCollapse(intent);
        }
    }
}
