"""Quick preview of expected VIBE scores for all demo products."""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.features.base_extractor import Review
from pipeline.scoring.score_aggregator import compute_vibe_score

SLUSHIE = [
    Review("I use this to make smoothies AND slushies! Total hack - game changer!", 5.0, source="amazon"),
    Review("TikTok showed me frozen lemonade in this thing. Absolute genius!", 5.0, source="amazon"),
    Review("You can also freeze coffee for the most amazing frappuccino.", 5.0, source="amazon"),
    Review("Didn't expect this to work as a sorbet maker but wow IT DOES!", 5.0, source="amazon"),
    Review("Hack: pour in pre-made juice, freeze, blend - perfect granita in minutes.", 5.0, source="amazon"),
    Review("I use it for dog's frozen treats now. Alternative uses are ENDLESS.", 4.0, source="amazon"),
    Review("My roommates discovered it makes incredible frozen margaritas. We use it every day.", 5.0, source="amazon"),
    Review("Someone on Instagram showed the slushie trick for protein shakes. Life changing.", 5.0, source="amazon"),
    Review("I am OBSESSED. Showed everyone at my BBQ and now 4 friends ordered it.", 5.0, source="amazon"),
    Review("I literally screamed when I first used this. Slushies come out PERFECT.", 5.0, source="amazon"),
    Review("Cannot stop talking about this. My entire office is now obsessed.", 5.0, source="amazon"),
    Review("This is the most fun kitchen appliance I have ever owned, no exaggeration.", 5.0, source="amazon"),
    Review("Posted a video of the slushie coming out and got 40k views overnight!", 5.0, source="amazon"),
    Review("Brought this to a pool party and it became the main event. Everyone wanted one.", 5.0, source="amazon"),
    Review("My kid thinks I am the coolest mom because of this machine.", 5.0, source="amazon"),
    Review("Filmed my first YouTube review just for this product. The swirl is SO satisfying.", 5.0, source="amazon"),
    Review("The color of the slushie = perfect thumbnail shot.", 5.0, source="amazon"),
    Review("The pour is incredibly photogenic. Every influencer in my feed has one now.", 4.0, source="amazon"),
    Review("Already bought three as gifts. Best housewarming present ever.", 5.0, source="amazon"),
    Review("Gave one to my sister AND my mom within a week of buying my own.", 5.0, source="amazon"),
    Review("If you are reading this review, just buy it. You will not regret it.", 5.0, source="amazon"),
    Review("Bought a second one for my office break room. My team loves it.", 5.0, source="amazon"),
    Review("Never seen anything like this. Thought slushies were only for gas stations.", 5.0, source="amazon"),
    Review("Blew my mind that this exists. How did we live without it?", 5.0, source="amazon"),
    Review("This is the first appliance that genuinely surprised me in years.", 5.0, source="amazon"),
    Review("For the price this is absolutely insane value. Expected to pay triple.", 5.0, source="amazon"),
    Review("Shocked at how affordable this is compared to what it delivers.", 4.0, source="amazon"),
    Review("Slushies are amazing but the machine is a bit loud. Still 5 stars.", 4.0, source="amazon"),
    Review("Cleans easily if you do it right after use. Slushie quality is unreal.", 5.0, source="amazon"),
    Review("My kids use it every single day after school. Worth every penny.", 5.0, source="amazon"),
]

CREAMI = [
    Review("This machine made me feel like a pastry chef. Better than Haagen-Dazs.", 5.0, source="amazon"),
    Review("I make protein ice cream every day now. The texture is incredible.", 5.0, source="amazon"),
    Review("TikTok was RIGHT about the Ninja Creami. Life will never be the same.", 5.0, source="amazon"),
    Review("I have made 40 different flavors in the past month. Cannot stop experimenting.", 5.0, source="amazon"),
    Review("Gifted one to my sister and she cried happy tears. That good.", 5.0, source="amazon"),
    Review("You can make Dole Whip at home with this. Disney fans will understand.", 5.0, source="amazon"),
    Review("Ice cream comes out so creamy and smooth. Posted a video and friends bombarded me.", 4.0, source="amazon"),
    Review("My nutritionist approved my protein ice cream recipe. Obsessed.", 5.0, source="amazon"),
    Review("Takes 24 hours to freeze but the wait is absolutely worth it every time.", 4.0, source="amazon"),
    Review("Kids think we own a gelato shop. Best parenting hack of the year.", 5.0, source="amazon"),
    Review("The crunchy mix-in feature is mind-blowing.", 5.0, source="amazon"),
    Review("Super loud when running but I forgive it because the results are amazing.", 3.0, source="amazon"),
    Review("Made mango sorbet from fresh fruit. Three ingredients. Perfection.", 5.0, source="amazon"),
    Review("Everyone at book club wanted the recipe when I brought my Creami ice cream.", 5.0, source="amazon"),
    Review("For the price it is worth every cent. Professional results at home.", 5.0, source="amazon"),
    Review("Would buy again. Have already bought two more as gifts.", 5.0, source="amazon"),
    Review("More complicated than expected but YouTube tutorials make it easy.", 3.0, source="amazon"),
    Review("Ice cream is SO much better than store-bought. Addicting to make.", 5.0, source="amazon"),
    Review("I can control exactly what goes in. Great for dietary restrictions.", 4.0, source="amazon"),
    Review("Ninja has completely changed my relationship with dessert.", 5.0, source="amazon"),
]

CHANEL_SAMPLE = [
    Review("The accessories are hot to the touch after use (5-star tester)", None, source="ihut"),
    Review("The oval brush when removing after use", None, source="ihut"),
    Review("The paddle brush seemed too hot to put away right after use", None, source="ihut"),
    Review("The unit feels slightly heavy when you've been styling for a while", None, source="ihut"),
    Review("Others are quick but the curlers take a while", None, source="ihut"),
    Review("The hair dryer alone is too heavy let alone with the accessories", None, source="ihut"),
    Review("It is compact and pleasant to see. You can keep it nicely in a suitcase", None, source="ihut"),
    Review("The oval brush is perfect for my hair type", None, source="ihut"),
    Review("I love how the accessories click in and out easily", None, source="ihut"),
    Review("The results are amazing - my hair has never been so smooth", None, source="ihut"),
]

print(f"\n{'='*60}")
print("EXPECTED VIBE SCORES FOR DEMO PRODUCTS")
print("=" * 60)

for label, revs in [
    ("[DEMO] Ninja Slushie Maker", SLUSHIE),
    ("[DEMO] Ninja Creami", CREAMI),
    ("[DEMO] Chanel (sample)", CHANEL_SAMPLE),
]:
    r = compute_vibe_score(revs)
    print(f"\n{label}")
    print(f"  VIBE Score: {r.vibe_score:5.1f}  [{r.score_band}]  confidence={r.confidence}")
    print(f"  Reviews: {len(revs)}")
    print("  Dimensions:")
    for dim, score in sorted(r.dimension_scores.items(), key=lambda x: -x[1]):
        shap = r.shap_values.get(dim, 0)
        shap_sign = "+" if shap >= 0 else ""
        print(f"    {dim:25s}: {score:5.1f}   SHAP {shap_sign}{shap:.2f}")
    print(f"  Baseline: {r.baseline_score}  SHAP sum: {sum(r.shap_values.values()):.2f}")
    print(f"  SHAP invariant: {r.baseline_score + sum(r.shap_values.values()):.1f} == {r.vibe_score}")
