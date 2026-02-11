import imdbinfo
import sys

# Default locations per country (capital city coords)
COUNTRY_LOCATIONS = {
    "FR": {"lat": "48.87", "long": "2.33"},
    "US": {"lat": "40.71", "long": "-74.01"},
    "GB": {"lat": "51.51", "long": "-0.13"},
    "DE": {"lat": "52.52", "long": "13.41"},
    "ES": {"lat": "40.42", "long": "-3.70"},
    "IT": {"lat": "41.90", "long": "12.50"},
    "CA": {"lat": "45.50", "long": "-73.57"},
    "JP": {"lat": "35.68", "long": "139.69"},
    "BR": {"lat": "-23.55", "long": "-46.63"},
    "AU": {"lat": "-33.87", "long": "151.21"},
}


def parse_locale(locale_str):
    """Parse 'fr-FR' into movie_locale='fr', wp_locale='fr-FR', country='FR', location."""
    if "-" in locale_str:
        lang, country = locale_str.split("-", 1)
    else:
        lang = locale_str
        country = locale_str.upper()

    wp_locale = f"{lang}-{country}"
    movie_locale = lang
    location = COUNTRY_LOCATIONS.get(country, {"lat": "48.87", "long": "2.33"})
    return movie_locale, wp_locale, country, location


def main():
    if len(sys.argv) < 2:
        print("Usage: python movie_info.py <imdb_id> [locale]")
        print("Example: python movie_info.py tt1375666")
        print("         python movie_info.py tt1375666 fr-FR")
        print("         python movie_info.py tt1375666 en-US")
        return

    imdb_id = sys.argv[1]
    locale_input = sys.argv[2] if len(sys.argv) > 2 else "fr-FR"
    movie_locale, wp_locale, country, location = parse_locale(locale_input)

    try:
        movie = imdbinfo.get_movie(imdb_id, locale=movie_locale)
        providers = imdbinfo.get_watch_providers(imdb_id, locale=wp_locale, location=location)

        print("-" * 50)
        print(f"TITLE:    {movie.title}")
        print(f"YEAR:     {movie.year}")
        print(f"GENRES:   {', '.join(movie.genres)}")
        print(f"SYNOPSIS: {movie.plot}")
        print(f"LOCALE:   {wp_locale} ({country})")
        print("-" * 50)

        print("STREAMING:")
        if providers.streaming:
            for p in providers.streaming:
                desc = f" ({p.description})" if p.description else ""
                print(f"  - {p.name}{desc}")
                print(f"    {p.link}")
        else:
            print("  None found.")

        print("\nRENT/BUY:")
        if providers.rent_buy:
            for p in providers.rent_buy:
                desc = f" ({p.description})" if p.description else ""
                print(f"  - {p.name}{desc}")
                print(f"    {p.link}")
        else:
            print("  None found.")
        print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
