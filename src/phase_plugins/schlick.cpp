#include <mitsuba/core/properties.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/phase.h>

NAMESPACE_BEGIN(mitsuba)
/*
    Isaac von Riedemann
    301423851
    imv@sfu.ca
*/
/**!

.. _phase-hg:

SchlickPhaseFunction phase function (:monosp:`schlick`)
-----------------------------------------------

.. pluginparameters::

 * - g
   - |float|
   - This parameter must be somewhere in the range -1 to 1
     (but not equal to -1 or 1). It denotes the *mean cosine* of scattering
     interactions. A value greater than zero indicates that medium interactions
     predominantly scatter incident light into a similar direction (i.e. the
     medium is *forward-scattering*), whereas values smaller than zero cause
     the medium to be scatter more light in the opposite direction.
   - |exposed|, |differentiable|, |discontinuous|



.. tabs::
    .. code-tab:: xml

        <phase type="schlick">
            <float name="g" value="0.1"/>
        </phase>

    .. code-tab:: python

        'type': 'schlick',
        'g': 0.1

*/
template <typename Float, typename Spectrum>
class SchlickPhaseFunction final : public PhaseFunction<Float, Spectrum> {
public:
    MI_IMPORT_BASE(PhaseFunction, m_flags, m_components)
    MI_IMPORT_TYPES(PhaseFunctionContext)

    SchlickPhaseFunction(const Properties &props) : Base(props) {
        ScalarFloat g = props.get<ScalarFloat>("g", 0.8f);
        if (g >= 1.f || g <= -1.f)
            Log(Error, "The asymmetry parameter must lie in the interval (-1, 1)!");
        m_g = g;

        m_flags = +PhaseFunctionFlags::Anisotropic;
        m_components.push_back(m_flags); // TODO: check
    }

    void traverse(TraversalCallback *callback) override {
        callback->put_parameter("g", m_g, ParamFlags::Differentiable |
                                          ParamFlags::Discontinuous);
    }
    // Update to evaluate the Schlick simplification
    MI_INLINE Float eval_schlick(Float cos_theta) const {
        Float num = 1.f - dr::square(m_g); 
        return num / (1.f + dr::square(m_g) - 2* m_g * cos_theta);
    }

    std::tuple<Vector3f, Spectrum, Float> sample(const PhaseFunctionContext & /* ctx */,
                                                 const MediumInteraction3f &mi,
                                                 Float /* sample1 */,
                                                 const Point2f &sample2,
                                                 Mask active) const override {
        MI_MASKED_FUNCTION(ProfilerPhase::PhaseFunctionSample, active);

        Float sqr_term  = (1.f - dr::square(m_g)) / (1.f - m_g + 2.f * m_g * sample2.x()),
              cos_theta = (1.f + dr::square(m_g) - dr::square(sqr_term)) / (2.f * m_g);

        // Diffuse fallback
        dr::masked(cos_theta, dr::abs(m_g) < dr::Epsilon<ScalarFloat>) = 1.f - 2.f * sample2.x();

        Float sin_theta = dr::safe_sqrt(1.f - dr::square(cos_theta));
        auto [sin_phi, cos_phi] = dr::sincos(2.f * dr::Pi<ScalarFloat> * sample2.y());

        Vector3f wo = mi.to_world(
            Vector3f(sin_theta * cos_phi, sin_theta * sin_phi, -cos_theta));

        return { wo, 1.f, eval_schlick(-cos_theta) };
    }

    std::pair<Spectrum, Float> eval_pdf(const PhaseFunctionContext & /* ctx */,
                                        const MediumInteraction3f &mi,
                                        const Vector3f &wo,
                                        Mask active) const override {
        MI_MASKED_FUNCTION(ProfilerPhase::PhaseFunctionEvaluate, active);
        Float pdf = eval_schlick(dr::dot(wo, mi.wi));
        return { pdf, pdf };
    }

    std::string to_string() const override {
        std::ostringstream oss;
        oss << "SchlickPhaseFunction[" << std::endl
            << "  g = " << string::indent(m_g) << std::endl
            << "]";
        return oss.str();
    }

    MI_DECLARE_CLASS()
private:
    Float m_g;
};

MI_IMPLEMENT_CLASS_VARIANT(SchlickPhaseFunction, PhaseFunction)
MI_EXPORT_PLUGIN(SchlickPhaseFunction, "SchlickPhaseFunction phase function")
NAMESPACE_END(mitsuba)
